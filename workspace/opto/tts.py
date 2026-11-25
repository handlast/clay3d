import asyncio, os, sys, edge_tts
p = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
for k in list(os.environ):
    if "proxy" in k.lower(): del os.environ[k]
async def m():
    c = edge_tts.Communicate(sys.argv[2], sys.argv[1], rate=sys.argv[4] if len(sys.argv)>4 else "+0%")
    await c.save(sys.argv[3])
asyncio.run(m())
