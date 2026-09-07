"""Explicit S1 purchasing candidates. Values/footprints stay schematic-authoritative.
DC-bias curves, lot availability and assembly process still require purchasing review.
"""
CAPS={
 'C1':('GRM21BR61E106KA73L','25V','https://www.farnell.com/datasheets/1747469.pdf'),
 'C2':('GRM21BR61E106KA73L','25V','https://www.farnell.com/datasheets/1747469.pdf'),
 'C9':('GRM21BR61E106KA73L','25V','https://www.farnell.com/datasheets/1747469.pdf'),
 'C10':('GRM21BR61E106KA73L','25V','https://www.farnell.com/datasheets/1747469.pdf'),
 'C17':('GRM21BR61A226ME44L','10V','https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61A226ME44-01A.pdf'),
 'C19':('GRM155R61A105KE15D','10V','https://www.murata.com/en-us/products/productdetail?partno=GRM155R61A105KE15D'),
 'C21':('CL31A107MQHNNNE','6.3V','https://product.samsungsem.com/mlcc/CL31A107MQHNNN.do')}
for r in ['C3','C5','C11','C13','C35']:CAPS[r]=('GRM188R61A106KAALD','10V','https://datasheet.octopart.com/GRM188R61A106KAALD-Murata-datasheet-138742814.pdf')
for r in ['C4','C12','C18','C20','C25','C29','C34']:CAPS[r]=('GRM155R71C104KA88D','16V','https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155R71C104KA88-01A.pdf')
for r in ['C36','C37']:CAPS[r]=('GRM188R71C104KA01D','16V','https://www.murata.com/en-us/products/productdetail?partno=GRM188R71C104KA01D')
for r in ['C6','C7','C8','C14','C15','C16']:CAPS[r]=('GRM31CR61C226KE15L','16V','https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM31CR61C226KE15-01A.pdf')
def apply(root,helpers):
 children,child,val,prop,q,node=helpers
 for s in children(root,'symbol'):
  ref=prop(s,'Reference');value=prop(s,'Value');fields={}
  if ref in CAPS:mpn,voltage,url=CAPS[ref];fields={'MPN':mpn,'Voltage':voltage,'Datasheet':url}
  elif ref.startswith('R'):
   existing={val(a[1]):val(a[2]) for a in children(s,'property')}
   if not existing.get('MPN'):
    code=value.replace('Ω','').replace('k','K').replace('.','')
    if '.' in value:
     a,b=value.replace('Ω','').split('.');code=a+('K' if 'k' in b else 'R')+b.rstrip('k')
    if code.isdigit():code+='R'
    fields={'MPN':'RC0402FR-07'+code+'L','Datasheet':'https://www.yageo.com/en/Product/Index/rchip/rc'}
  elif ref in ['SW2','SW3','SW7']:fields={'MPN':'TS-1187A-B-A-B','Datasheet':'https://www.helloxkb.com/Home/Goods/goodsInfoxq/id/1913'}
  elif ref=='J1':fields={'MPN':'B2B-PH-SM4-TB(LF)(SN)'}
  elif ref=='J2':fields={'MPN':'TYPE-C-31-M-12','Datasheet':'https://www.lcsc.com/datasheet/C165948.pdf'}
  elif ref.startswith(('U','Q')):fields={'MPN':value}
  for key,value in fields.items():
   entry=next((a for a in children(s,'property') if val(a[1])==key),None)
   if entry is not None:entry[2]=q(value)
   else:s.append(node(f'(property {q(key)} {q(value)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'))
