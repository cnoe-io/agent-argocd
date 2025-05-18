from a2a.client import A2AClient
from typing import Any
from uuid import uuid4
from a2a.types import (
    SendMessageResponse,
    GetTaskResponse,
    SendMessageSuccessResponse,
    Task,
    TaskState,
    SendMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
    SendStreamingMessageRequest,
)
import httpx
import traceback

AGENT_URL = 'http://localhost:10000'


def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {
        'message': {
            'role': 'user',
            'parts': [{'type': 'text', 'text': text}],
            'messageId': uuid4().hex,
        },
    }

    if task_id:
        payload['message']['taskId'] = task_id

    if context_id:
        payload['message']['contextId'] = context_id
    return payload


def print_json_response(response: Any, description: str) -> None:
    """Helper function to print the JSON representation of a response."""
    print(f'--- {description} ---')
    if hasattr(response, 'root'):
        print(f'{response.root.model_dump_json(exclude_none=True)}\n')
    else:
        print(f'{response.model_dump(mode="json", exclude_none=True)}\n')


async def run_single_turn_test(client: A2AClient) -> None:
    """Runs a single-turn non-streaming test."""

    send_payload = create_send_message_payload(
        text='What is argocd version?',
    )
    request = SendMessageRequest(params=MessageSendParams(**send_payload))

    print('--- Single Turn Request ---')
    # Send Message
    send_response: SendMessageResponse = await client.send_message(request)
    print_json_response(send_response, 'Single Turn Request Response')
    if not isinstance(send_response.root, SendMessageSuccessResponse):
        print('received non-success response. Aborting get task ')
        return

    if not isinstance(send_response.root.result, Task):
        print('received non-task response. Aborting get task ')
        return

    task_id: str = send_response.root.result.id
    # print('---Query Task---')
    # # query the task
    # get_request = GetTaskRequest(params=TaskQueryParams(id=task_id))
    # get_response: GetTaskResponse = await client.get_task(get_request)
    # print_json_response(get_response, 'Query Task Response')


async def run_streaming_test(client: A2AClient) -> None:
    """Runs a single-turn streaming test."""

    send_payload = create_send_message_payload(
      text='If you add 15 to the product of 8 and 7, then subtract 10, what is the result?',
    )

    request = SendStreamingMessageRequest(
        params=MessageSendParams(**send_payload)
    )

    print('--- Single Turn Streaming Request ---')
    stream_response = client.send_message_streaming(request)
    async for chunk in stream_response:
        print_json_response(chunk, 'Streaming Chunk')


async def run_multi_turn_test(client: A2AClient) -> None:
  """Runs a complex multi-turn non-streaming math problem test (add and multiply only)."""
  print('--- Multi-Turn Complex Math Problem Request ---')

  # --- First Turn ---
  first_turn_payload = create_send_message_payload(
    text='I have 4 apples. I buy 3 more. How many apples do I have now?'
  )
  request1 = SendMessageRequest(
    params=MessageSendParams(**first_turn_payload)
  )
  first_turn_response: SendMessageResponse = await client.send_message(request1)
  print_json_response(first_turn_response, 'Multi-Turn: First Turn Response')

  context_id: str | None = None
  task_id: str | None = None
  if isinstance(first_turn_response.root, SendMessageSuccessResponse) and isinstance(first_turn_response.root.result, Task):
    task: Task = first_turn_response.root.result
    context_id = task.contextId
    task_id = task.id

    # --- Second Turn ---
    print('--- Multi-Turn: Second Turn ---')
    second_turn_payload = create_send_message_payload(
      text='Now, I buy 2 more apples. How many apples do I have in total?',
      task_id=task_id,
      context_id=context_id
    )
    request2 = SendMessageRequest(
      params=MessageSendParams(**second_turn_payload)
    )
    second_turn_response: SendMessageResponse = await client.send_message(request2)
    print_json_response(second_turn_response, 'Multi-Turn: Second Turn Response')

    # --- Third Turn (Multiplication) ---
    if isinstance(second_turn_response.root, SendMessageSuccessResponse) and isinstance(second_turn_response.root.result, Task):
      task2: Task = second_turn_response.root.result
      context_id2 = task2.contextId
      task_id2 = task2.id

      print('--- Multi-Turn: Third Turn (Multiplication) ---')
      third_turn_payload = create_send_message_payload(
        text='If I put all my apples into bags of 3, how many bags do I have?',
        task_id=task_id2,
        context_id=context_id2
      )
      request3 = SendMessageRequest(
        params=MessageSendParams(**third_turn_payload)
      )
      third_turn_response: SendMessageResponse = await client.send_message(request3)
      print_json_response(third_turn_response, 'Multi-Turn: Third Turn Response')

      # --- Fourth Turn (Addition) ---
      if isinstance(third_turn_response.root, SendMessageSuccessResponse) and isinstance(third_turn_response.root.result, Task):
        task3: Task = third_turn_response.root.result
        context_id3 = task3.contextId
        task_id3 = task3.id

        print('--- Multi-Turn: Fourth Turn (Addition) ---')
        fourth_turn_payload = create_send_message_payload(
          text='If I find 5 more apples and add them to my collection, how many apples do I have now?',
          task_id=task_id3,
          context_id=context_id3
        )
        request4 = SendMessageRequest(
          params=MessageSendParams(**fourth_turn_payload)
        )
        fourth_turn_response: SendMessageResponse = await client.send_message(request4)
        print_json_response(fourth_turn_response, 'Multi-Turn: Fourth Turn Response')
      else:
        print('Third turn did not return a valid task for further input.')
    else:
      print('Second turn did not return a valid task for further input.')
  else:
    print('First turn did not return a valid task for further input.')


async def main() -> None:
    """Main function to run the tests."""
    print(f'Connecting to agent at {AGENT_URL}...')
    try:
        async with httpx.AsyncClient() as httpx_client:
            client = await A2AClient.get_client_from_agent_card_url(
                httpx_client, AGENT_URL
            )
            print('Connection successful.')

            await run_single_turn_test(client)
            # await run_streaming_test(client)
            # await run_multi_turn_test(client)

    except Exception as e:
        traceback.print_exc()
        print(f'An error occurred: {e}')
        print('Ensure the agent server is running.')


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
