import asyncio


class AsyncIterator:
    def __init__(self, list):
        self.list = list
        self.end = len(list) - 1
        self.start = -1

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.start < self.end:
            if self.start / 2 == 1:
                await asyncio.sleep(2)
            self.start += 1
            return self.list[self.start]
        else:
            raise StopAsyncIteration

my_list = ['some1', 'some2', 'some3', 'some4', 'some5']

my_async_iterator = AsyncIterator(my_list)


async def do_magic():
    async for i in my_async_iterator:
        print(i)


if __name__ == '__main__':
    asyncio.run(do_magic())
