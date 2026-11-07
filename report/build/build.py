import sys, importlib, json
sys.path.insert(0, '/tmp/claude-0/-home-user-script/87268cc6-2f55-530f-ae80-f44e6c5415c4/scratchpad/build')
from builder import *
import content as C
importlib.reload(C)
OUT = sys.argv[1]
TOCPAGES = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}

b = B('/tmp/claude-0/-home-user-script/87268cc6-2f55-530f-ae80-f44e6c5415c4/scratchpad/src/tpl.docx')
M = C.META
def L(t, **k): return b.p([t], align=k.pop('align', 'center'), size=k.pop('size', 18), bold=k.pop('bold', True), **k)

def cover_bottom():
    L(f"รายงานฉบับนี้เป็นส่วนหนึ่งของรายวิชา{M['subject']} รหัสวิชา {M['code']}")
    L(f"ภาคเรียนที่ {M['term']}  ปีการศึกษา {M['year']}")
    L(M['school'])

# ---- ปกนอก
b.logo()
L('เรื่อง ' + C.TITLE, size=20)
b.blank(9)
L('โดย')
L(M['cover_author'])
b.blank(3)
L('เสนอ'); L(M['teacher'])
b.blank(8)
cover_bottom()
# ---- หน้ารองปก (ว่าง)
b.p([], align='center', size=18, bold=True, pb_before=True)
# ---- ปกใน
b.logo(pb_before=True)
L(C.TITLE, size=20)
b.blank(7)
L('จัดทำโดย')
for line in M['members']:
    L(line)
L(M['class_line'])
b.blank(3)
L('เสนอ'); L(M['teacher'])
b.blank(5 - max(0, len(M['members']) - 5))
cover_bottom()
# ---- คำนำ
L('คำนำ', pb_before=True)
b.blank(1)
runs = [{'t': '\t' + C.PREFACE[0]}, {'t': C.TITLE, 'hl': 'yellow'}, {'t': C.PREFACE[1]},
        {'t': C.PREFACE[2], 'hl': 'cyan'}, {'t': C.PREFACE[3]}]
b.p(runs, align='thaiDistribute', size=16)
for par in C.PREFACE_MORE:
    b.p(['\t' + par], align='thaiDistribute', size=16)
b.p([], align='thaiDistribute', size=16); b.p([], align='thaiDistribute', size=16)
b.p(['คณะผู้จัดทำ' if M['group'] else 'ผู้จัดทำ'], align='right', size=16)
# ---- สารบัญ
L('สารบัญ', pb_before=True)
b.p([], align='center', size=16, bold=True)
RT = [('right', 6.27, None)]
b.p([{'t': 'เรื่อง\tหน้า', 'bold': True}], size=16, tabs=RT)
b.p([], size=6)
def toc(text, pg, bold=False, ind=False):
    b.p([{'t': ('     ' if ind else '') + text + '\t' + pg, 'bold': bold}], size=16, tabs=RT)
toc('คำนำ', 'ก', True); toc('สารบัญ', 'ข', True)
toc(C.TITLE, TOCPAGES.get('TITLE', '๑'), True)
for h in [x[1] for x in C.BODY if x[0] == 'h1']:
    toc(h, TOCPAGES.get(h, '?'), ind=True)
toc('บรรณานุกรม', TOCPAGES.get('BIB', '?'), True)
toc('ภาคผนวก', TOCPAGES.get('APP', '?'), True)
b.end_section(b.sect_break('A4', pgnum={'fmt': 'thaiLetters', 'start': 1}))

# ---- เนื้อหา
hdr = b.make_header()
F = NEW
first = True
b.p([C.TITLE], align='center', size=20, bold=True, font=F, after=12, keep=True)
img_no = 0
for item in C.BODY:
    k = item[0]
    if k == 'h1':
        b.p([item[1]], size=18, bold=True, font=F, before=0 if first else 12, after=0, keep=True); first = False
    elif k == 'h2':
        b.p([item[1]], size=16, bold=True, font=F, left=0.5, keep=True)
    elif k == 'p':
        b.p([item[1]], size=16, font=F, first=0.5, align='thaiDistribute')
    elif k == 'img':
        img_no += 1
        _, path, w, cap, src = item
        b.image(path, w)
        b.p([f'ภาพที่ {th(img_no)} {cap}'], align='center', size=14, font=F, keep=True)
        b.p([src], align='center', size=14, font=F, after=8)
    elif k == 'pb':
        b.p([], font=F, pb_before=True)
# ---- บรรณานุกรม
b.p(['บรรณานุกรม'], align='center', size=18, bold=True, font=F, pb_before=True, after=12)
for e in C.BIB:
    runs = [dict(t=e['pre']), dict(t=e['title'], bold=True), dict(t=e['post'])]
    b.p(runs, size=16, font=F, left=0.5, hanging=0.5, after=4, align='left')
b.end_section(b.sect_break('Letter', header_ref=hdr, pgnum={'fmt': 'thaiNumbers', 'start': 1}))
# ---- หน้าคั่นภาคผนวก
b.p(['ภาคผนวก'], align='center', size=18, bold=True, font=F, before=294)
b.end_section(b.sect_break('Letter', header_ref=hdr))
# ---- เนื้อหาภาคผนวก
for item in C.APPENDIX:
    k = item[0]
    if k == 'h1': b.p([item[1]], size=18, bold=True, font=F, keep=True, after=6, align=item[2] if len(item) > 2 else None)
    elif k == 'h2': b.p([item[1]], size=16, bold=True, font=F, left=0.5, keep=True)
    elif k == 'p': b.p([item[1]], size=16, font=F, first=0.5, align='thaiDistribute')
    elif k == 'term': b.p([dict(t=item[1], bold=True), dict(t=' ' + item[2])], size=16, font=F, left=0.5, hanging=0.5, align='thaiDistribute', after=2)
    elif k == 'img':
        img_no += 1
        _, path, w, cap, src = item
        b.image(path, w)
        b.p([f'ภาพที่ {th(img_no)} {cap}'], align='center', size=14, font=F, keep=True)
        b.p([src], align='center', size=14, font=F, after=10)
    elif k == 'pb': b.p([], font=F, pb_before=True)
final = b.sect_break('Letter', header_ref=hdr)
b.save(OUT, final)
print('saved', OUT)
