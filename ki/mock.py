import openai
import asyncio


class AsyncChatCompletionIterator:
    def __init__(self, answer: str):
        self.answer_index = 0
        self.answer_deltas = answer.split(" ")

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.answer_index < len(self.answer_deltas):
            answer_chunk = self.answer_deltas[self.answer_index] + " "
            self.answer_index += 1
            return await asyncio.create_task(self.delay_answer(answer_chunk))
        else:
            raise StopAsyncIteration
        
    async def delay_answer(self, answer_chunk):
        await asyncio.sleep(0.05)
        return openai.util.convert_to_openai_object(
            {"choices": [{"delta": {"content": answer_chunk}}]})


async def mock_acreate(*args, **kwargs):
    return AsyncChatCompletionIterator("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam cursus tincidunt dui. In sit amet laoreet metus. Cras vehicula, risus vel placerat ultricies, magna lacus porta urna, quis dictum lacus augue at tortor. Nulla bibendum, nibh et varius porta, nunc mi tempor tortor, non posuere velit augue condimentum purus. Aenean commodo eu ipsum in gravida. Praesent imperdiet pharetra eros, in mattis dui maximus vitae. In sed auctor ante. Vestibulum eu pharetra metus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur vitae pulvinar elit. Sed efficitur ac odio at sagittis. Morbi id commodo neque. Vestibulum viverra vestibulum est, eget sagittis dolor fringilla sed. Praesent rutrum est cursus diam ultrices, in vestibulum diam tincidunt. Vestibulum blandit, lectus sit amet consequat dignissim, dolor diam gravida dolor, ac dictum urna turpis non sapien. Nulla facilisi. Vestibulum id massa in nisi dictum porttitor. Aenean eu justo accumsan, viverra mi sit amet, auctor ligula. Praesent gravida vestibulum tellus eget venenatis.")
