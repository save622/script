import sys, json, re
sys.path.insert(0, '/tmp/claude-0/-home-user-script/87268cc6-2f55-530f-ae80-f44e6c5415c4/scratchpad/build')
from builder import *
import content4 as C
OUT = sys.argv[1]
PG = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}

# ---- เลขภาพตามลำดับที่วางในเอกสาร
ORDER = []
for item in C.BODY + C.APPENDIX:
    if item[0] == 'img': ORDER.append(item[1])
    elif item[0] == 'grid': ORDER.extend(item[1])
assert len(ORDER) == len(set(ORDER)), 'ภาพซ้ำ'
NUM = {k: th(i + 1) for i, k in enumerate(ORDER)}
def R(s):
    s = re.sub(r'\{N:(\w+)\}', lambda m: NUM[m.group(1)], s)
    s = re.sub(r'\{P:(\w+)\}', lambda m: PG.get('img:' + m.group(1), '?'), s)
    return s
def cap(k):
    path, c, src, short = C.IMGS[k]
    return path, R(f'ภาพที่ {NUM[k]} {c}'), src

b = B('/tmp/claude-0/-home-user-script/87268cc6-2f55-530f-ae80-f44e6c5415c4/scratchpad/src/tpl.docx')
M = C.META
def L(t, **k): return b.p([t], align=k.pop('align', 'center'), size=k.pop('size', 18), bold=k.pop('bold', True), **k)
def cover_bottom():
    L(f"รายงานฉบับนี้เป็นส่วนหนึ่งของรายวิชา{M['subject']} รหัสวิชา {M['code']}")
    L(f"ภาคเรียนที่ {M['term']}  ปีการศึกษา {M['year']}")
    L(M['school'])

# ---- ปกนอก
b.logo(); L('เรื่อง ' + C.TITLE, size=20); b.blank(9)
L('โดย'); L(M['cover_author']); b.blank(3)
L('เสนอ'); L(M['teacher']); b.blank(8)
cover_bottom()
# ---- หน้ารองปก
b.p([], align='center', size=18, bold=True, pb_before=True)
# ---- ปกใน
b.logo(pb_before=True); L(C.TITLE, size=20); b.blank(7)
L('จัดทำโดย')
for line in M['members']: L(line)
L(M['class_line']); b.blank(3)
L('เสนอ'); L(M['teacher']); b.blank(5 - max(0, len(M['members']) - 5))
cover_bottom()
# ---- คำนำ
L('คำนำ', pb_before=True); b.blank(1)
b.p([{'t': '\t' + C.PREFACE[0]}, {'t': C.TITLE, 'hl': 'yellow'}, {'t': C.PREFACE[1]},
     {'t': C.PREFACE[2], 'hl': 'cyan'}, {'t': C.PREFACE[3]}], align='thaiDistribute', size=16)
for par in C.PREFACE_MORE: b.p(['\t' + par], align='thaiDistribute', size=16)
b.p([], align='thaiDistribute', size=16); b.p([], align='thaiDistribute', size=16)
b.p(['คณะผู้จัดทำ' if M['group'] else 'ผู้จัดทำ'], align='right', size=16)
# ---- สารบัญ
RT = [('right', 6.27, None)]
L('สารบัญ', pb_before=True); b.p([], align='center', size=16, bold=True)
b.p([{'t': 'เรื่อง\tหน้า', 'bold': True}], size=16, tabs=RT); b.p([], size=6)
def toc(text, pg, bold=False, ind=False):
    b.p([{'t': ('     ' if ind else '') + text + '\t' + pg, 'bold': bold}], size=16, tabs=RT)
toc('คำนำ', 'ก', True); toc('สารบัญ', 'ข', True); toc('สารบัญภาพ', 'ค', True)
toc(C.TITLE, PG.get('TITLE', '๑'), True)
for h in [x[1] for x in C.BODY if x[0] == 'h1']: toc(h, PG.get(h, '?'), ind=True)
toc('บรรณานุกรม', PG.get('BIB', '?'), True)
toc('ภาคผนวก', PG.get('APP', '?'), True)
for x in C.APPENDIX:
    if x[0] == 'ah': toc(x[2], PG.get(x[2], '?'), ind=True)
# ---- สารบัญภาพ
L('สารบัญภาพ', pb_before=True); b.p([], align='center', size=16, bold=True)
b.p([{'t': 'ภาพที่\tหน้า', 'bold': True}], size=16, tabs=RT); b.p([], size=6)
for k in ORDER:
    short = C.IMGS[k][3]
    b.p([{'t': f'ภาพที่ {NUM[k]} {short}\t' + PG.get('img:' + k, '?')}], size=16, tabs=RT)
b.end_section(b.sect_break('A4', pgnum={'fmt': 'thaiLetters', 'start': 1}))

# ---- เนื้อหา
hdr = b.make_header()
F = NEW
first = True
b.p([C.TITLE], align='center', size=20, bold=True, font=F, after=12, keep=True)
def put_img(k, w, maxh=2.8):
    path, c, src = cap(k)
    b.image(path, w, max_h_in=maxh)
    b.p([c], align='center', size=14, font=F, keep=True)
    b.p([src], align='center', size=14, font=F, after=8)
for item in C.BODY:
    k = item[0]
    if k == 'h1':
        b.p([item[1]], size=18, bold=True, font=F, before=0 if first else 12, keep=True); first = False
    elif k == 'h2': b.p([item[1]], size=16, bold=True, font=F, left=0.5, keep=True)
    elif k == 'p': b.p([R(item[1])], size=16, font=F, first=0.5, align='thaiDistribute')
    elif k == 'img': put_img(item[1], item[2], item[3] if len(item) > 3 else 2.8)
    elif k == 'grid':
        grid(b, [cap(x) for x in item[1]], F, max_h=item[2])
b.p(['บรรณานุกรม'], align='center', size=18, bold=True, font=F, pb_before=True, after=12)
from docx.opc.constants import RELATIONSHIP_TYPE as RTY
for e in C.BIB:
    post = e['post']; url = None
    m = re.search(r'(https?://\S+)$', post)
    if m: url = m.group(1); post = post[:m.start()]
    para = b.p([dict(t=e['pre']), dict(t=e['title'], bold=True), dict(t=post)], size=16, font=F, left=0.5, hanging=0.5, after=4, align='left', keep_lines=True)
    if url:
        rid = b.d.part.relate_to(url, RTY.HYPERLINK, is_external=True)
        hl = el('w:hyperlink'); hl.set(qn('r:id'), rid)
        rr = el('w:r'); rr.append(rpr(F, 16)); tt = el('w:t'); tt.text = url; rr.append(tt); hl.append(rr)
        para.append(hl)
b.end_section(b.sect_break('Letter', header_ref=hdr, pgnum={'fmt': 'thaiNumbers', 'start': 1}))
# ---- หน้าคั่นภาคผนวก (กลางหน้า)
b.p(['ภาคผนวก'], align='center', size=18, bold=True, font=F, before=294)
b.end_section(b.sect_break('Letter', header_ref=hdr))
# ---- หน้ารวมภาพ
for item in C.APPENDIX:
    k = item[0]
    if k == 'ah': b.p([item[1]], align='center', size=18, bold=True, font=F, keep=True, after=6, pb_before=len(item) > 3)
    elif k == 'anote': b.p([R(item[1])], size=16, font=F, first=0.5, align='thaiDistribute', after=8, keep=True)
    elif k == 'img': put_img(item[1], item[2], item[3] if len(item) > 3 else 2.8)
    elif k == 'grid': grid(b, [cap(x) for x in item[1]], F, max_h=item[2])
    elif k == 'pb': b.p([], font=F, pb_before=True)
cp = b.d.core_properties; cp.author = ''; cp.last_modified_by = ''; cp.title = C.TITLE; cp.comments = ''
b.save(OUT, b.sect_break('Letter', header_ref=hdr))
json.dump({'ORDER': ORDER, 'NUM': NUM}, open(OUT + '.imgs.json', 'w'), ensure_ascii=False)
print('saved', OUT, 'images', len(ORDER))
