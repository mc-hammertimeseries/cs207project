import asyncio

async def main(pk, row, arg):
    return proc_main(pk, row, arg)

def proc_main(pk, row, arg):
    #print("[[[[[[[[[[[STATS]]]]]]]]]]]]", pk, row, arg)
    damean = row['ts'].mean()
    dastd = row['ts'].std()
    return [damean, dastd]