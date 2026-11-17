rm -f test_*.png; python3 film.py test "$@" && python3 -c "
from PIL import Image
import glob
fs=sorted(glob.glob('test_*.png')); n=len(fs); c=min(9,n); r=(n+c-1)//c
s=Image.new('RGB',(216*c,384*r))
for i,f in enumerate(fs): s.paste(Image.open(f).resize((216,384)),((i%c)*216,(i//c)*384))
s.save('sheet.png')"
