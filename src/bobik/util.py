def print_events(event):
    if "messages" in event:
        message = event["messages"][-1]

        if message.type in ["system", "human"]:
            return

        if type(message.content) == list:
            for msg in message.content:
                print(msg.get("text", ""))
        else:
            print(message.content)

        print("")
