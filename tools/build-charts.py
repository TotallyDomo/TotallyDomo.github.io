"""Rebuild the blog's seven editorial SVG charts from their recorded data."""

from pathlib import Path
from html import escape
from math import cos, sin, pi, sqrt, floor
import json
import re

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'static/img/posts'
BG, FG, MUTED, GRID = '#0d1117', '#e6edf3', '#8b98a9', '#2a313c'
INK = '#191917'
COPPER, SAND, SLATE, STONE = '#dfa06e', '#b9ac94', '#798f94', '#baaea0'
SANS, MONO = 'Segoe UI, system-ui, -apple-system, BlinkMacSystemFont, sans-serif', 'Consolas, monospace'
MANIFEST = []


class _Svg:
    def __init__(self, title, subtitle, number, height=760):
        self.height, self.parts = height, []
        self.rect(0, 0, 1200, height, BG)
        self.text(1140, 43, f'FIG. {number:02}', 18, MUTED, MONO, 'end')
        self.text(60, 94, title, 46, FG, SANS)
        self.text(60, 139, subtitle, 22, MUTED)

    def text(self, x, y, value, size=22, color=FG, font=SANS, anchor='start'):
        value = escape(str(value)).replace('[delta]', '&#916;')
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" text-anchor="{anchor}" style="font-variant-numeric:lining-nums tabular-nums">{value}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, width=1, extra=''):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>')

    def rect(self, x, y, w, h, color):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')

    def dot(self, x, y, r, color, extra=''):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" {extra}/>')

    def path(self, data, color, width=2, fill='none', extra=''):
        self.parts.append(f'<path d="{data}" stroke="{color}" stroke-width="{width}" fill="{fill}" {extra}/>')

    def pie(self, cx, cy, radius, values, colors, labels=None, font_size=22, start=-pi/2):
        total, angle = sum(values), start
        assert total > 0 and all(v >= 0 for v in values)
        for i, (value, color) in enumerate(zip(values, colors)):
            if not value:
                continue
            end = angle + 2*pi*value/total
            sx, sy = cx+radius*cos(angle), cy+radius*sin(angle)
            ex, ey = cx+radius*cos(end), cy+radius*sin(end)
            # WHY: omit separator strokes on tiny slices so they remain truthful slivers.
            border = 0 if value/total < .01 else 1.2
            self.path(f'M {cx} {cy} L {sx} {sy} A {radius} {radius} 0 {int(end-angle > pi)} 1 {ex} {ey} Z', BG, border, color)
            if labels and labels[i]:
                mid = (angle+end)/2
                self.text(cx+radius*.64*cos(mid), cy+radius*.64*sin(mid)+7, labels[i], font_size, INK, anchor='middle')
            angle = end

    def legend(self, entries, y):
        for x, label, color in entries:
            self.rect(x, y-16, 15, 15, color)
            self.text(x+27, y, label, 21, MUTED)

    def save(self, name, description):
        content = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{self.height}" viewBox="0 0 1200 {self.height}" role="img" aria-labelledby="title desc"><title id="title">{escape(name)}</title><desc id="desc">{escape(description)}</desc>'+''.join(self.parts)+'</svg>'
        target = ASSETS / (name+'.svg')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='ascii', errors='xmlcharrefreplace')
        # WHY: explicit SVG pairs follow the site's manual toggle, not the OS theme.
        light = content
        for dark, replacement in [(BG, '#ffffff'), (FG, '#1f2328'), (MUTED, '#59636e'), (GRID, '#d1d9e0')]:
            light = light.replace(dark, replacement)
        # Preserve data fills. Direct labels need darker ink on a white page.
        label_colors = {COPPER: '#945022', STONE: '#665b4e', SLATE: '#425f65'}
        light = re.sub(r'<text\b[^>]*>', lambda m: next(
            (m[0].replace(f'fill="{c}"', f'fill="{v}"') for c, v in label_colors.items() if f'fill="{c}"' in m[0]), m[0]), light)
        for color, replacement in label_colors.items():
            light = light.replace(f'stroke="{color}"', f'stroke="{replacement}"')
        target.with_suffix('.light.svg').write_text(light, encoding='ascii', errors='xmlcharrefreplace')
        MANIFEST.append({'name': name, 'height': self.height})


def _context():
    s = _Svg('Cost per turn', 'Warm 15K prefix. Each turn writes 1K tokens and generates 500.', 1)
    s.text(60, 178, 'Pie area scales with total cost.', 20, MUTED)
    for turn, cx in [(1,230),(50,590),(100,970)]:
        values = [1.5+(turn-1)*.1, 2, 2.5]
        total = sum(values)
        r = 165*sqrt(total/15.9)
        assert abs(pi*r*r/total - pi*165*165/15.9) < 1e-8
        s.text(cx, 244, f'Turn {turn}', 24, anchor='middle')
        s.text(cx, 285, f'{total:g}K TC', 31, anchor='middle')
        s.pie(cx, 474, r, values, [COPPER,SAND,SLATE], [f'{v:g}K' for v in values], 21)
    s.legend([(248,'Cache reads',COPPER),(510,'Cache writes',SAND),(790,'Output',SLATE)], 717)
    s.save('tokenomics/context-growth-cost', 'Area-proportional pies at turns 1, 50 and 100. Total cost is 6K, 10.9K and 15.9K token credits (TC). Reads cost 1.5K, 6.4K and 11.4K TC. Writes stay at 2K and output at 2.5K. Rates: 0.1 TC/read token, 2 TC/write token, 5 TC/output token. After turn one, the 1K writes include the previous response. No cache expiry or compaction.')


def _startup():
    s = _Svg('Startup context cost', '100 turns: one write at 2 TC/token, 99 reads at 0.1 TC/token.', 2, 660)
    s.text(110,190,'Cumulative cost / thousand TC',19,MUTED)
    xy = lambda t,v: (110+(t-1)/99*690,548-v/600*330)
    for v in [0,200,400,600]:
        _,y = xy(1,v)
        s.line(110,y,800,y)
        s.text(89,y+6,v,19,MUTED,MONO,'end')
    for t in [1,25,50,75,100]:
        x,_ = xy(t,0)
        s.text(x,583,t,19,MUTED,MONO,'middle')
    s.text(455,624,'Model turns',20,MUTED,anchor='middle')
    for p,c in [(45,STONE),(15,COPPER)]:
        a,b = xy(1,p*2),xy(100,p*11.9)
        s.line(*a,*b,c,3)
        s.dot(*b,4.5,c)
        s.text(866,b[1]-13,f'{p}K-token prefix',22,c)
        s.text(866,b[1]+23,f'{p*11.9:g}K TC',29,c)
    upper,lower = xy(100,535.5)[1],xy(100,178.5)[1]
    mid = (upper+lower)/2
    s.line(828,upper,844,upper,MUTED,1.5)
    s.line(838,upper,838,lower,MUTED,1.5)
    s.line(828,lower,844,lower,MUTED,1.5)
    s.line(838,mid,854,mid,MUTED,1.5)
    s.text(866,mid+10,'[delta] 357K TC',32,COPPER)
    s.save('tokenomics/cold-boot-comparison','Cumulative startup-prefix cost only. A 15K prefix costs 178.5K TC over 100 turns. A 45K prefix costs 535.5K TC. Difference 357K TC. Both stay cached. Task-specific tokens are excluded.')


def _keepalive():
    s = _Svg('The cost of waiting', '800K cached tokens. 1h TTL. Keep-alive every 55 minutes.', 3, 800)
    s.text(60,178,'Read: 0.1 TC/token. Rewrite: 2 TC/token.',20,MUTED)
    s.text(60,239,'After four hours',29,FG,SANS)
    s.text(645,239,'Longer waits',29,FG,SANS)
    s.text(60,282,'Cold resume: 1.6M TC',20,MUTED)
    # INVARIANT: the whole pie is the cold-resume budget, not combined spending.
    s.pie(300,480,155,[.4,1.2],[COPPER,STONE])
    s.text(367,427,'25%',31,INK,anchor='middle')
    s.text(250,528,'75%',38,INK,anchor='middle')
    s.line(410,370,435,346,COPPER,1.5)
    s.text(439,330,'Keep warm',22,COPPER)
    s.text(439,367,'400K TC',28,COPPER)
    s.line(190,590,135,659,STONE,1.5)
    s.text(60,695,'Avoided cost',22,STONE)
    s.text(60,735,'1.2M TC',31,STONE)
    x = lambda mins: 670+(mins-60)/(1200-60)*435
    y = lambda cost: 605-cost/2*280
    for v in [0,.8,1.6]:
        s.line(670,y(v),1105,y(v))
        s.text(656,y(v)+6,f'{v:g}',18,MUTED,anchor='end')
    for h in [1,4,8,12,16,20]:
        s.text(x(h*60),636,h,18,MUTED,anchor='middle')
    s.text(670,282,'Million TC',18,MUTED)
    s.text(887,677,'Wait / hours',20,MUTED,anchor='middle')
    s.line(670,y(1.6),1105,y(1.6),STONE,2,'stroke-dasharray="7 6"')
    s.text(670,y(1.6)-14,'Cold resume',20,STONE)
    points=[(60,.16)]
    level=.16
    for m in range(110,1201,55):
        points.extend([(m,level),(m,level+.08)])
        level+=.08
    points.append((1200,level))
    d='M '+' L '.join(f'{x(t)} {y(c)}' for t,c in points)
    s.path(d,COPPER,3)
    s.text(865,568,'Keep-alives + resume',20,COPPER)
    s.dot(x(1045),y(1.6),5,COPPER)
    s.text(1110,727,'Equal cost at 17h 25m',22,COPPER,anchor='end')
    s.text(1110,759,'19 keep-alives + resume',19,MUTED,anchor='end')
    assert (floor(240/55)+1)*80000==400000
    assert 20*80000==1600000
    s.save('tokenomics/keep-alive-payoff','Illustrative waiting costs for an already-warm 800K-token prefix. The whole pie is the 1.6M TC cold-resume budget. After four hours, keeping warm plus resume costs 400K TC, one quarter of that budget. The other 1.2M TC, 75%, is avoided cost. Scheduled keep-alives every 55 minutes, each costing 80K TC. The modeled step reaches 1.6M TC after 19 keep-alives plus resume, at 1045 minutes. Every read hits. Initial warm-up, extra messages and output overhead are excluded.')


def _builds():
    s = _Svg('Full-corpus build time', '39,056 pages. Identical output. June 28 measurements.', 1, 730)
    s.text(270,232,'Python / 385.7 s',28,anchor='middle')
    s.pie(270,426,150,[245.4,140.3],[COPPER,STONE],['245.4 s','140.3 s'],23)
    s.legend([(70,'Reread for hashes + counts',COPPER)],638)
    s.legend([(70,'Other build work',STONE)],678)
    x = lambda seconds: 760+seconds/400*340
    s.text(760,232,'Elapsed / seconds',23,MUTED)
    for seconds in [0,200,400]:
        s.line(x(seconds),275,x(seconds),603)
        s.text(x(seconds),641,seconds,19,MUTED,MONO,'middle')
    for label,detail,total,y in [('Python','',385.7,300),('C++','',67.6,390),('Go','1 worker',62.9,480),('Go','8 workers',38.0,570)]:
        s.text(565,y+7,label,24)
        if detail:
            s.text(565,y+33,detail,19,MUTED)
        s.line(x(0),y,x(total),y,STONE,2)
        s.dot(x(total),y,6,STONE)
        s.text(x(total)+15,y+7,f'{total:.1f}',23)
    assert abs(245.4+140.3-385.7)<1e-9
    s.save('unity-corpus/build-shootout','Full-corpus build times from the preserved June 28 manifests. Python 385.7 seconds, including 245.4 seconds rereading output to hash and count it, and 140.3 seconds of other work. C++ 67.6 seconds. Single-threaded Go 62.9 seconds. Eight-worker Go 38.0 seconds. The four finish markers share a linear zero-based seconds axis. The separate pie shows the Python breakdown only. Python was a one-shot implementation.')


def _spend():
    s = _Svg('Building vs. shipping', 'Measured through July 13. Split at the July 9 publication date.', 2, 725)
    for cx,title,values,labels,total in [(340,'Billed tokens',[229,527],['229M','527M'],'756M tokens'),(880,'List-price equivalent',[346,908],['$346','$908'],'$1,254')]:
        s.text(cx,232,title,25,anchor='middle')
        s.text(cx,271,total,29,anchor='middle')
        s.pie(cx,461,155,values,[SLATE,COPPER])
        angle=-pi/2
        for value,label in zip(values,labels):
            mid=angle+pi*value/sum(values)
            tx,ty=cx+99*cos(mid),461+99*sin(mid)
            s.text(tx,ty-3,f'{value/sum(values):.0%}',32,INK,anchor='middle')
            s.text(tx,ty+28,label,22,INK,anchor='middle')
            angle+=2*pi*value/sum(values)
    s.legend([(285,'Building',SLATE),(600,'Validation + shipping',COPPER)],683)
    s.save('unity-corpus/spend-split','Composition of recorded spend split at the July 9 public date. Building: 229M of 756M billed tokens (30%) and $346 of $1254 list-price equivalent (28%). Validating and shipping: 527M tokens (70%) and $908 (72%). The two pies use different units and compare shares only, not total area. Work ran on flat-rate subscriptions.')


def _recall():
    s = _Svg('Recall by ranker and representation', 'Top-10 recall. 1,008 cases. Values rounded to whole percent.', 3, 740)
    s.legend([(445,'All cases',STONE),(735,'Concept pages',COPPER)],201)
    x=lambda v: 350+v*7.3
    for v in [0,25,50,75,100]:
        s.line(x(v),248,x(v),611)
        s.text(x(v),645,f'{v}%',18,MUTED,anchor='middle')
    rows=[('Naive scan','Raw HTML',94,59,275),('Naive scan','Derived Markdown',95,62,365),('BM25 index','Raw HTML',97,96,455),('BM25 index','The corpus',97,96,545)]
    for ranker,rep,all_cases,concept,y in rows:
        s.text(60,y-4,ranker,24)
        s.text(60,y+24,rep,20,MUTED)
        s.line(x(concept),y,x(all_cases),y,STONE,3)
        s.dot(x(all_cases),y,6,STONE)
        s.dot(x(concept),y,6,COPPER)
        s.text(x(all_cases),y-17,all_cases,22,STONE,anchor='middle')
        s.text(x(concept),y+30,concept,22,COPPER,anchor='middle')
    s.text(715,699,'Top-10 recall',21,MUTED,anchor='middle')
    s.save('unity-corpus/ranker-vs-representation','Paired-dot comparison transcribed at the original chart precision. Naive scan over raw HTML: 94% all cases and 59% concept pages. Naive scan over derived Markdown: 95% and 62%. BM25 over raw HTML: 97% and 96%. BM25 over the corpus: 97% and 96%. These whole-percent labels must not be read as evidence of exact equality between the BM25 representations.')


def _vibemax():
    s = _Svg('Session cost breakdown', 'Two demo runs. Visible text estimated from characters.', 1, 1070)
    # WHY: these are the two published demo sessions, not the A/B means.
    records=[('Style off',450,168145,10017,3352,308,66),('Vibemax on',935,374142,13473,4637,156.5,130)]
    for label,cx,*_ in records:
        s.text(cx,209,label,27,anchor='middle')
    colors=[STONE,'#a28a66',SLATE,COPPER,'#eee9df']
    for row,cy,title in [(0,395,'Billed tokens'),(1,785,'List-price USD')]:
        compositions=[]
        for label,cx,reads,writes,output,visible,uncached in records:
            values=[reads,writes,output-visible,visible,uncached]
            if row:
                values=[reads*.1/1e6,writes*2/1e6,(output-visible)*5/1e6,visible*5/1e6,uncached/1e6]
            compositions.append(values)
        maximum=max(sum(v) for v in compositions)
        s.text(60,cy-23,title,24)
        s.text(60,cy+12,'Area = cost' if row else 'Area = tokens',18,MUTED)
        for (_,cx,*_),values in zip(records,compositions):
            total=sum(values)
            r=132*sqrt(total/maximum)
            total_label=f'${total:.3f}' if row else f'{total/1000:.0f}K tokens'
            s.text(cx,cy-157,total_label,29,anchor='middle')
            # WHY: rotate each pie to center the visible-text slice at 3 o'clock.
            preceding=sum(values[:3])/total
            start=-2*pi*(preceding+values[3]/total/2)
            s.pie(cx,cy,r,values,colors,start=start)
            pct=values[3]/total*100
            detail=f'{pct:.1f}% / ${values[3]:.4f}' if row else f'{pct:.2f}% / {records[0 if cx==450 else 1][5]:g} tokens'
            s.line(cx+r,cy,cx+r+18,cy,COPPER,1.5)
            s.line(cx+r+18,cy,cx+r+18,cy+150,COPPER,1.5)
            s.text(cx,cy+180,detail,22,COPPER,anchor='middle')
    s.legend([(70,'Cache reads',STONE),(355,'Cache writes','#a28a66'),(650,'Other output',SLATE),(915,'Visible text',COPPER)],1030)
    s.save('vibemax-output-style-wont-save-you-money/session-cost-composition','Four proportional-area pies, with area scales separate for tokens and dollars. Source: grid-haiku-t1-blind-r02 and grid-haiku-t1-vibemax-r06. Off: 168145 cached reads, 10017 writes, 3352 output, 66 uncached input, 308 estimated visible tokens. On: 374142 reads, 13473 writes, 4637 output, 130 input, 156.5 estimated visible tokens. Visible text is estimated as characters divided by four. Historical illustrative list rates per million tokens: $0.10 cached read, $2 cache write, $5 output, $1 uncached input. Totals are computed from the usage buckets at those rates, not the harness cost field. Visible text is 2.9% and 0.9% of dollars. Other output includes tool calls and reasoning. These two sessions are not an estimate of the style effect.')


def main():
    """Write all SVG sources and the render manifest, failing on invalid data."""
    for build in [_context,_startup,_keepalive,_builds,_spend,_recall,_vibemax]:
        build()
    (ROOT/'tools/chart-manifest.json').write_text(json.dumps(MANIFEST,indent=2)+'\n',encoding='ascii')
    print(f'Built {len(MANIFEST)} SVG charts.')


if __name__ == '__main__':
    main()
