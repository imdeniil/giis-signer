package ru.voskhod.crypto.impl;

import com.ctc.wstx.stax.WstxEventFactory;
import com.ctc.wstx.stax.WstxInputFactory;
import com.ctc.wstx.stax.WstxOutputFactory;
import org.apache.xml.security.signature.XMLSignatureInput;
import org.apache.xml.security.transforms.Transform;
import org.apache.xml.security.transforms.TransformSpi;
import org.apache.xml.security.transforms.TransformationException;

import javax.xml.stream.XMLEventFactory;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLEventWriter;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.Characters;
import javax.xml.stream.events.EndElement;
import javax.xml.stream.events.Namespace;
import javax.xml.stream.events.StartElement;
import javax.xml.stream.events.XMLEvent;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Stack;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Класс, реализующий алгоритм трансформации "urn://smev-gov-ru/xmldsig/transform" для Apache Santuario.
 *
 * @author dpryakhin
 */
public class SmevTransformSpi extends TransformSpi {
    private static final Logger logger = Logger.getLogger(SmevTransformSpi.class.getName());

    public static final String ALGORITHM_URN = "urn://smev-gov-ru/xmldsig/transform";
    private static final String ENCODING_UTF_8 = "UTF-8";

    private static final AttributeSortingComparator attributeSortingComparator = new AttributeSortingComparator();

    private static final ThreadLocal<XMLInputFactory> inputFactory = ThreadLocal.withInitial(WstxInputFactory::new);
    private static final ThreadLocal<XMLOutputFactory> outputFactory = ThreadLocal.withInitial(WstxOutputFactory::new);
    private static final ThreadLocal<XMLEventFactory> eventFactory = ThreadLocal.withInitial(WstxEventFactory::new);

    @Override
    protected String engineGetURI() {
        return ALGORITHM_URN;
    }

    @Override
    protected XMLSignatureInput enginePerformTransform(XMLSignatureInput argInput,
                                                       OutputStream argOutput, Transform argTransform) throws IOException, TransformationException {
        if (argOutput == null)
            return enginePerformTransform(argInput);
        else {
            if (logger.isLoggable(Level.FINE)) {
                ByteArrayOutputStream debug = new ByteArrayOutputStream();
                MultiplexOutputStream mos = new MultiplexOutputStream(argOutput);
                mos.addOutputStream(debug);
                process(argInput.getOctetStream(), mos);
                logger.fine("Transformation result:\n" + new String(debug.toByteArray()));
            } else {
                process(argInput.getOctetStream(), argOutput);
            }
            XMLSignatureInput result = new XMLSignatureInput((byte[]) null);
            result.setOutputStream(argOutput);
            return result;
        }
    }

    @Override
    protected XMLSignatureInput enginePerformTransform(XMLSignatureInput argInput,
                                                       Transform argTransform) throws IOException, TransformationException {
        return enginePerformTransform(argInput);
    }

    @Override
    protected XMLSignatureInput enginePerformTransform(XMLSignatureInput argInput) throws IOException, TransformationException {

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        process(argInput.getOctetStream(), result);
        byte[] postTransformData = result.toByteArray();

        return new XMLSignatureInput(postTransformData);
    }

    @SuppressWarnings("unchecked")
    public void process(InputStream argSrc, OutputStream argDst) throws TransformationException {
        Stack<List<Namespace>> prefixMappingStack = new Stack<>();
        XMLEventReader src = null;
        XMLEventWriter dst = null;
        try {
            src = inputFactory.get().createXMLEventReader(argSrc, ENCODING_UTF_8);
            dst = outputFactory.get().createXMLEventWriter(argDst, ENCODING_UTF_8);
            XMLEventFactory factory = eventFactory.get();

            int prefixCnt = 1;
            while (src.hasNext()) {
                XMLEvent event = src.nextEvent();
                if (event.isCharacters()) {
                    final Characters characters = event.asCharacters();
                    String data = characters.getData();
                    logger.fine("Text Data:\n" + data);
                    // Отсекаем whitespace symbols.
                    if (!data.trim().isEmpty()) {
                        dst.add(event);
                    }
                } else if (event.isStartElement()) {
                    List<Namespace> myPrefixMappings = new LinkedList<>();
                    prefixMappingStack.push(myPrefixMappings);

                    // Обработка элемента: NS prefix rewriting.
                    // N.B. Элементы в unqualified form не поддерживаются.
                    StartElement srcEvent = (StartElement) event;
                    String nsURI = srcEvent.getName().getNamespaceURI();
                    String prefix = findPrefix(nsURI, prefixMappingStack);

                    if (prefix == null) {
                        prefix = "ns" + prefixCnt++;
                        myPrefixMappings.add(factory.createNamespace(prefix, nsURI));
                    }
                    StartElement dstEvent = factory.createStartElement(prefix, nsURI, srcEvent.getName().getLocalPart());
                    dst.add(dstEvent);

                    // == Обработка атрибутов. Два шага: отсортировать, промэпить namespace URI. ==
                    Iterator<Attribute> srcAttributeIterator = srcEvent.getAttributes();
                    // Положим атрибуты в list, чтобы их можно было отсортировать.
                    List<Attribute> srcAttributeList = new LinkedList<>();
                    while (srcAttributeIterator.hasNext()) {
                        srcAttributeList.add(srcAttributeIterator.next());
                    }
                    // Сортировка атрибутов по алфавиту.
                    srcAttributeList.sort(attributeSortingComparator);

                    // Обработка префиксов. Аналогична обработке префиксов элементов,
                    // за исключением того, что у атрибут может не иметь namespace.
                    List<Attribute> dstAttributeList = new LinkedList<>();
                    for (Attribute srcAttribute : srcAttributeList) {
                        String attributeNsURI = srcAttribute.getName().getNamespaceURI();
                        String attributeLocalName = srcAttribute.getName().getLocalPart();
                        String value = srcAttribute.getValue();
                        Attribute dstAttribute;
                        if (attributeNsURI != null && !"".equals(attributeNsURI)) {
                            String attributePrefix = findPrefix(attributeNsURI, prefixMappingStack);
                            if (attributePrefix == null) {
                                attributePrefix = "ns" + prefixCnt++;
                                myPrefixMappings.add(factory.createNamespace(attributePrefix, attributeNsURI));
                            }
                            dstAttribute = factory.createAttribute(attributePrefix, attributeNsURI, attributeLocalName, value);
                        } else {
                            dstAttribute = factory.createAttribute(attributeLocalName, value);
                        }
                        dstAttributeList.add(dstAttribute);
                    }

                    // Вывести namespace prefix mappings для текущего элемента.
                    // Их порядок детерминирован, т.к. перед мэппингом атрибуты были отсортированы.
                    // Поэтому дополнительной сотрировки здесь не нужно.
                    for (Namespace mapping : myPrefixMappings) {
                        dst.add(mapping);
                    }

                    // Вывести атрибуты.
                    // N.B. Мы не выводим атрибуты сразу вместе с элементом, используя метод
                    // XMLEventFactory.createStartElement(prefix, nsURI, localName, List<Namespace>, List<Attribute>),
                    // потому что при использовании этого метода порядок атрибутов в выходном документе
                    // меняется произвольным образом.
                    for (Attribute attr : dstAttributeList) {
                        dst.add(attr);
                    }
                } else if (event.isEndElement()) {
                    // Гарантируем, что empty tags запишутся в форме <a></a>, а не в форме <a/>.
                    dst.add(eventFactory.get().createSpace(""));

                    // NS prefix rewriting
                    EndElement srcEvent = (EndElement) event;
                    String nsURI = srcEvent.getName().getNamespaceURI();
                    String prefix = findPrefix(nsURI, prefixMappingStack);
                    if (prefix == null) {
                        throw new TransformationException("EndElement: prefix mapping is not found for namespace " + nsURI);
                    }

                    EndElement dstEvent = eventFactory.get().createEndElement(prefix, nsURI, srcEvent.getName().getLocalPart());
                    dst.add(dstEvent);

                    prefixMappingStack.pop();
                }
                // Атрибуты обрабатываются в событии startElement.

                // Остальные события (processing instructions, start document, etc.) опускаем.
            }
        } catch (XMLStreamException e) {
            Object[] exArgs = {e.getMessage()};
            throw new TransformationException("Can not perform transformation " + ALGORITHM_URN, exArgs, e);
        } finally {
            if (src != null) {
                try {
                    src.close();
                } catch (XMLStreamException e) {
                    logger.log(Level.WARNING, "Can not close XMLEventReader", e);
                }
            }
            if (dst != null) {
                try {
                    dst.close();
                } catch (XMLStreamException e) {
                    logger.log(Level.WARNING, "Can not close XMLEventWriter", e);
                }
            }
            try {
                argSrc.close();
            } catch (IOException e) {
                logger.log(Level.WARNING, "Can not close input stream.", e);
            }
            if (argDst != null) {
                try {
                    argDst.close();
                } catch (IOException e) {
                    logger.log(Level.WARNING, "Can not close output stream.", e);
                }
            }
        }
    }

    private static String findPrefix(String argNamespaceURI, Stack<List<Namespace>> argMappingStack) {
        if (argNamespaceURI == null) {
            throw new IllegalArgumentException("No namespace элементы не поддерживаются.");
        }

        for (List<Namespace> elementMappingList : argMappingStack) {
            for (Namespace mapping : elementMappingList) {
                if (argNamespaceURI.equals(mapping.getNamespaceURI())) {
                    return mapping.getPrefix();
                }
            }
        }
        return null;
    }

    private static class AttributeSortingComparator implements Comparator<Attribute> {
        @Override
        public int compare(Attribute x, Attribute y) {
            String xNS = x.getName().getNamespaceURI();
            String xLocal = x.getName().getLocalPart();
            String yNS = y.getName().getNamespaceURI();
            String yLocal = y.getName().getLocalPart();

            // Оба атрибута - unqualified.
            if (empty(xNS) && empty(yNS)) {
                return xLocal.compareTo(yLocal);
            }

            // Оба атрибута - qualified.
            if (!empty(xNS) && !empty(yNS)) {
                // Сначала сравниваем namespaces.
                int nsComparisonResult = xNS.compareTo(yNS);
                if (nsComparisonResult != 0) {
                    return nsComparisonResult;
                } else {
                    // Если равны - local names.
                    return xLocal.compareTo(yLocal);
                }
            }

            // Один - qualified, второй - unqualified.
            if (empty(xNS)) {
                return 1;
            } else {
                return -1;
            }
        }

        private static boolean empty(String arg) {
            return arg == null || "".equals(arg);
        }
    }
}
