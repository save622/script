import copy, re, sys, importlib
import docx
from docx.shared import Pt, Inches, Emu
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

TH = str.maketrans('0123456789', '๐๑๒๓๔๕๖๗๘๙')
def th(s): return str(s).translate(TH)

PSK = 'TH SarabunPSK'; NEW = 'TH Sarabun New'

def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items(): e.set(qn('w:' + k), str(v))
    return e

def rpr(font, size, bold=False, highlight=None, lang_th=False):
    r = el('w:rPr')
    r.append(el('w:rFonts', ascii=font, hAnsi=font, cs=font, eastAsia=font))
    if bold: r.append(el('w:b')); r.append(el('w:bCs'))
    if highlight: r.append(el('w:highlight', val=highlight))
    r.append(el('w:sz', val=int(size * 2))); r.append(el('w:szCs', val=int(size * 2)))
    if lang_th: r.append(el('w:lang', val='th-TH', bidi='th-TH'))
    else: r.append(el('w:lang', val='en-US', bidi='th-TH'))
    return r

class B:
    def __init__(self, tpl):
        self.d = docx.Document(tpl)
        body = self.d.element.body
        paras = body.findall(qn('w:p'))
        self.logo_run = copy.deepcopy(paras[0].find(qn('w:r')))
        self.final_sect = copy.deepcopy(body.find(qn('w:sectPr')))
        for c in list(body): body.remove(c)
        self.body = body

    def p(self, runs=(), align=None, style='a5', first=None, left=None, hanging=None,
          before=None, after=None, keep=False, pb_before=False, tabs=None, font=PSK, size=16,
          bold=False, keep_lines=False, widow=True):
        p = el('w:p'); pp = el('w:pPr'); p.append(pp)
        if style: pp.append(el('w:pStyle', val=style))
        if keep: pp.append(el('w:keepNext'))
        if keep_lines: pp.append(el('w:keepLines'))
        if pb_before: pp.append(el('w:pageBreakBefore'))
        if tabs:
            t = el('w:tabs')
            for kind, pos, leader in tabs:
                a = dict(val=kind, pos=int(pos * 1440))
                if leader: a['leader'] = leader
                t.append(el('w:tab', **a))
            pp.append(t)
        if before is not None or after is not None:
            pp.append(el('w:spacing', before=int((before or 0) * 20), after=int((after or 0) * 20), line=240, lineRule='auto'))
        ind = {}
        if left is not None: ind['left'] = int(left * 1440)
        if first is not None: ind['firstLine'] = int(first * 1440)
        if hanging is not None: ind['hanging'] = int(hanging * 1440)
        if ind: pp.append(el('w:ind', **ind))
        if align: pp.append(el('w:jc', val=align))
        pp.append(rpr(font, size, bold))
        for r in runs:
            if isinstance(r, str): r = dict(t=r)
            rr = el('w:r'); rr.append(rpr(r.get('font', font), r.get('size', size), r.get('bold', bold), r.get('hl')))
            parts = r['t'].split('\t')
            for i, part in enumerate(parts):
                if i: rr.append(el('w:tab'))
                for j, sub in enumerate(part.split('\u2011')):
                    if j: rr.append(el('w:noBreakHyphen'))
                    if sub:
                        t = el('w:t'); t.text = sub; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); rr.append(t)
            p.append(rr)
        self.body.append(p); return p

    def blank(self, n=1, size=18, align='center', font=PSK):
        for _ in range(n): self.p([], align=align, size=size, bold=True, font=font)

    def logo(self, pb_before=False):
        p = self.p([], align='center', size=18, bold=True, pb_before=pb_before)
        p.append(copy.deepcopy(self.logo_run)); return p

    def sect_break(self, kind, header_ref=None, pgnum=None, valign=None, title_pg=False):
        """end current section: put sectPr into a new empty paragraph"""
        sp = el('w:sectPr')
        if header_ref: sp.append(el('w:headerReference', **{'type': 'default'}) ); sp[-1].set(qn('r:id'), header_ref)
        sp.append(el('w:type', val='nextPage'))
        if kind == 'A4':
            sp.append(el('w:pgSz', w=11906, h=16838))
            sp.append(el('w:pgMar', top=1440, right=1440, bottom=1440, left=1440, header=708, footer=708, gutter=0))
        else:  # Letter body
            sp.append(el('w:pgSz', w=12240, h=15840))
            sp.append(el('w:pgMar', top=2160, right=1440, bottom=1440, left=2160, header=720, footer=720, gutter=0))
        if pgnum: sp.append(el('w:pgNumType', **pgnum))
        sp.append(el('w:cols', space=708))
        if valign: sp.append(el('w:vAlign', val=valign))
        sp.append(el('w:docGrid', linePitch=360))
        return sp

    def end_section(self, sp):
        last = self.body.findall(qn('w:p'))[-1]
        pPr = last.find(qn('w:pPr'))
        pPr.insert(len(pPr) - 1 if pPr.find(qn('w:rPr')) is not None else len(pPr), sp)

    def make_header(self):
        from docx.opc.constants import RELATIONSHIP_TYPE as RT
        from docx.opc.packuri import PackURI
        from docx.opc.part import XmlPart
        from docx.oxml import parse_xml
        xml = ('<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
               'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
               '<w:p><w:pPr><w:pStyle w:val="a5"/><w:jc w:val="right"/></w:pPr>'
               '<w:fldSimple w:instr=" PAGE "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/>'
               '<w:sz w:val="32"/><w:szCs w:val="32"/><w:lang w:val="th-TH" w:bidi="th-TH"/></w:rPr><w:t>๑</w:t></w:r></w:fldSimple></w:p></w:hdr>')
        part = XmlPart(PackURI('/word/header1.xml'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml',
                       parse_xml(xml), self.d.part.package)
        return self.d.part.relate_to(part, RT.HEADER)

    def image(self, path, width_in, max_h_in=2.8):
        im = Image.open(path); w, h = im.size
        wi = width_in; hi = wi * h / w
        if hi > max_h_in: hi = max_h_in; wi = hi * w / h
        p = self.p([], align='center', font=NEW, keep=True)
        tmp = docx.Document()
        r = self.d.add_paragraph().add_run()
        r.add_picture(path, width=Inches(wi))
        par = r._r.getparent(); par.getparent().remove(par)
        p.append(r._r)
        return p

    def save(self, out, final_sp):
        self.body.append(final_sp)
        self.d.save(out)

def _pic_run(b, path, w_in, max_h):
    im = Image.open(path); w, h = im.size
    wi = w_in; hi = wi * h / w
    if hi > max_h: wi = max_h * w / h
    r = b.d.add_paragraph().add_run(); r.add_picture(path, width=Inches(wi))
    par = r._r.getparent(); par.getparent().remove(par)
    return r._r

def grid(b, items, font, cols=2, total_w=6.0, max_h=2.6, cap_size=14):
    """borderless table, each cell: image, caption, source"""
    tbl = el('w:tbl'); pr = el('w:tblPr')
    pr.append(el('w:tblW', w=int(total_w*1440), type='dxa')); pr.append(el('w:jc', val='center'))
    bd = el('w:tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'): bd.append(el('w:'+side, val='nil'))
    pr.append(bd); pr.append(el('w:tblLayout', type='fixed'))
    tbl.append(pr)
    g = el('w:tblGrid'); cw = int(total_w*1440/cols)
    for _ in range(cols): g.append(el('w:gridCol', w=cw))
    tbl.append(g)
    for i in range(0, len(items), cols):
        tr = el('w:tr'); trpr = el('w:trPr'); trpr.append(el('w:cantSplit')); tr.append(trpr)
        for it in items[i:i+cols] + [None]*(cols-len(items[i:i+cols])):
            tc = el('w:tc'); tcp = el('w:tcPr'); tcp.append(el('w:tcW', w=cw, type='dxa')); tc.append(tcp)
            if it is None:
                p = b.p([], font=font); b.body.remove(p); tc.append(p)
            else:
                path, cap, src = it
                p1 = b.p([], align='center', font=font, keep=True); b.body.remove(p1)
                p1.append(_pic_run(b, path, total_w/cols - 0.25, max_h)); tc.append(p1)
                p2 = b.p([cap], align='center', size=cap_size, font=font, keep=True); b.body.remove(p2); tc.append(p2)
                p3 = b.p([src], align='center', size=cap_size-1, font=font, after=8); b.body.remove(p3); tc.append(p3)
            tr.append(tc)
        tbl.append(tr)
    b.body.append(tbl)
    b.p([], font=font, size=8)
