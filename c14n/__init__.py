from lxml.etree import (_ElementTree, _Comment, _XSLTProcessingInstruction,
                        _Element)


class StringElem:
    def __init__(self,
                 tag,
                 prefix=None,
                 nsmap=None,
                 attrib=None,
                 end=False) -> None:
        self.tag = self._prepare_tag(tag)
        self.nsmap = nsmap
        self.prefix = prefix
        self.attrib = attrib
        self.end = end

    def __str__(self) -> str:
        return self._build_str()

    def _build_str(self) -> str:
        base = '</' if self.end else '<'

        if self.prefix:
            base += f'{self.prefix}:{self.tag}'
        else:
            base += self.tag

        if self.nsmap:
            base += ' ' + ' '.join(self.nsmap)
        if self.attrib:
            base += ' ' + ' '.join(self.attrib)

        base += '>'
        return base

    def _prepare_tag(self, tag) -> str:
        try:
            ns_end = tag.index('}') + 1
            return tag[ns_end:]
        except ValueError:
            return tag


class C14NTransform:
    def __init__(self, xml) -> None:
        self.xml = self.__getroot(xml)
        self.start_pi = None
        self.end_pi = None
        self.__read_pi()
        self.rows = []

    def __getroot(self, xml) -> _Element:
        if isinstance(xml, _ElementTree):
            return xml.getroot()
        return xml

    def __read_pi(self) -> None:
        start_pi = self.xml.getprevious()
        if isinstance(start_pi, _XSLTProcessingInstruction):
            self.start_pi = self._do_pinode(start_pi) + '\n'

        end_pi = self.xml.getnext()
        if isinstance(start_pi, _XSLTProcessingInstruction):
            self.end_pi = '\n' + self._do_pinode(end_pi)

    def canonicalize(self) -> str:
        if self.start_pi is not None:
            self.rows.append(self.start_pi)

        start_tag = StringElem(self.xml.tag,
                               prefix=self.xml.prefix,
                               nsmap=self._do_namespaces(self.xml),
                               attrib=self._do_attributes(self.xml))
        self.rows.append(str(start_tag))

        if self.xml.text is not None:
            self.rows.append(self._do_tag_text(self.xml.text))

        self._iter_children(self.xml)

        end_tag = StringElem(self.xml.tag,
                             prefix=self.xml.prefix,
                             end=True)
        self.rows.append(str(end_tag))

        if self.xml.tail is not None:
            self.rows.append(self.xml.tail)

        if self.end_pi is not None:
            self.rows.append(self.end_pi)

        return ''.join(self.rows)

    def _iter_children(self, xml) -> None:
        for child_node in xml.getchildren():
            if isinstance(child_node, _Comment):
                if child_node.tail is not None:
                    self.rows.append(child_node.tail)
                continue
            start_tag = StringElem(child_node.tag,
                                   prefix=child_node.prefix,
                                   nsmap=self._do_namespaces(child_node, xml),
                                   attrib=self._do_attributes(child_node))
            self.rows.append(str(start_tag))

            if child_node.text is not None:
                self.rows.append(self._do_tag_text(child_node.text))

            self._iter_children(child_node)

            end_tag = StringElem(child_node.tag,
                                 prefix=child_node.prefix,
                                 end=True)
            self.rows.append(str(end_tag))

            if child_node.tail is not None:
                self.rows.append(child_node.tail)

    def _do_pinode(self, pi_node) -> str:
        base = f'<?{pi_node.target}'

        if pi_node.text:
            base += f' {pi_node.text}'

        base += '?>'
        return base

    def _do_namespaces(self, node, parent_node=None) -> list:
        ns_unique = []
        ns_unique_named = []

        def __ns_to_str(k, v) -> None:
            if k is None:
                ns_unique.append(f'xmlns="{v}"')
            else:
                ns_unique_named.append(f'xmlns:{k}="{v}"')

        for k, v in node.nsmap.items():
            if parent_node is not None:
                parent_ns = parent_node.nsmap.get(k)
                if k is None and parent_ns is None:
                    parent_ns = ''
                if parent_ns is None or parent_ns != v:
                    __ns_to_str(k, v)
            else:
                __ns_to_str(k, v)

        ns_unique_named.sort()
        ns_unique.extend(ns_unique_named)
        return ns_unique

    def _do_attributes(self, node) -> list:
        attrs = []
        attr_keys = list(node.attrib.keys())
        attr_keys.sort()

        def __get_ns_key(ns) -> str:
            ns = ns.strip('{}')
            for k, v in node.nsmap.items():
                if v == ns:
                    return k

        for attr_key in attr_keys:
            attr_val = self._do_attr_text(node.attrib[attr_key])
            try:
                ns_end = attr_key.index('}') + 1
                ns_key = __get_ns_key(attr_key[:ns_end])
                attr_key = f'{ns_key}:{attr_key[ns_end:]}'
            except ValueError:
                pass
            attrs.append(f'{attr_key}="{attr_val}"')
        return attrs

    def _do_tag_text(self, txt) -> str:
        txt = txt.replace("&", "&amp;")
        txt = txt.replace("<", "&lt;")
        txt = txt.replace(">", "&gt;")
        txt = txt.replace("\015", "&#xD;")
        return txt

    def _do_attr_text(self, txt) -> str:
        txt = txt.replace("&", "&amp;")
        txt = txt.replace("<", "&lt;")
        txt = txt.replace('"', '&quot;')
        txt = txt.replace('\011', '&#x9')
        txt = txt.replace('\012', '&#xA')
        txt = txt.replace('\015', '&#xD')
        return txt


def canonicalize(xml) -> str:
    c14nrender = C14NTransform(xml)
    return c14nrender.canonicalize()
