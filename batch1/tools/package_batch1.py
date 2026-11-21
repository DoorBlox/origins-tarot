"""Build a test-world datapack ZIP and a combined KubeJS/server bundle."""
from zipfile import ZipFile,ZIP_DEFLATED
from pathlib import Path
R=Path(__file__).resolve().parents[1]
OUT=R/'output'
OUT.mkdir(exist_ok=True)
def create_zip(name,files):
 with ZipFile(OUT/name,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for file,arc in sorted(files):
   z.write(file,arc)
 with ZipFile(OUT/name) as z:
  if z.testzip() is not None:raise RuntimeError('Corrupt generated archive')
 print(OUT/name)
def tree(prefix):
 return [(f,str(f.relative_to(R))) for f in (R/prefix).rglob('*') if f.is_file()]
create_zip('Tarot_Arcane_Batch1_Fool_Datapack_1.18.2.zip',
 [(f,str(f.relative_to(R/'datapack'))) for f in (R/'datapack').rglob('*') if f.is_file()])
create_zip('Tarot_Arcane_Batch1_Server_Bundle.zip',tree('kubejs')+tree('datapack')+
 [(f,str(f.relative_to(R))) for f in (R/'docs').glob('BATCH_1_*.md')]+
 [(R/'README_BATCH_1.md','README_BATCH_1.md')])
