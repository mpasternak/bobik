def print_events(events):
    for event in events:
        if "messages" in event:
            message = event["messages"][-1]
            if message.type in ["system", "tool", "human"]:
                continue
            print(message.content)
