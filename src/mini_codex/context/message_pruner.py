from mini_codex.context.token_counter import TokenCounter
from mini_codex.model.messages import Message

class MessagePruner:
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter

    def group_messages(self, messages: list[Message]) -> list[list[Message]]:
        """
        Group messages so that an assistant tool call and all its
        corresponding tool results are treated as one atomic unit.
        """
        groups: list[list[Message]] = []
        i = 0

        while i < len(messages):
            message = messages[i]
            if message.role == "assistant" and message.tool_calls:
                expected_ids = {call.id for call in message.tool_calls}
                group = [message]
                received_ids = set()
                i += 1

                while i < len(messages) and received_ids != expected_ids:
                    result_message = messages[i]

                    if (
                        result_message.role != "tool"
                        or result_message.tool_call_id not in expected_ids
                        or result_message.tool_call_id in received_ids
                    ):
                        raise ValueError(
                            "Invalid tool message sequence: "
                            "tool results must match the preceding assistant tool calls"
                        )

                    group.append(result_message)
                    received_ids.add(result_message.tool_call_id)
                    i += 1

                if received_ids != expected_ids:
                    raise ValueError("Incomplete tool call group")

                groups.append(group)
                continue

            if message.role == "tool":
                raise ValueError("Orphan tool result without a preceding assistant tool call")

            groups.append([message])
            i += 1

        return groups

    def prune(
        self,
        messages: list[Message],
        max_tokens: int,
    ) -> list[Message]:
        if max_tokens < 0:
            raise ValueError("max_tokens must be non-negative")

        if not messages:
            return []

        groups = self.group_messages(messages)

        # Preserve the original user request as the task instruction.
        pinned_group = groups[0] if groups[0][0].role == "user" else []

        pinned_tokens = self.token_counter.estimate_messages(pinned_group)
        if pinned_tokens > max_tokens:
            raise ValueError(
                "The initial user message exceeds the available context budget"
            )

        selected_groups = []
        used_tokens = pinned_tokens

        # Keep the newest groups first, then restore chronological order.
        for group in reversed(groups[len(pinned_group):]):
            group_tokens = self.token_counter.estimate_messages(group)

            if used_tokens + group_tokens > max_tokens:
                break

            selected_groups.append(group)
            used_tokens += group_tokens

        selected_groups.reverse()

        return [
            message
            for group in [pinned_group, *selected_groups]
            for message in group
        ]