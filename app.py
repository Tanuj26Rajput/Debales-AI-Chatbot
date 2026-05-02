import os
os.environ["USER_AGENT"] = "debales-ai-agent/1.0"

from graph.workflow import build_graph


app = build_graph()

while True:
    query = input("\nAsk something: ")

    # This state object is passed through all graph nodes.
    result = app.invoke({
        "query": query,
        "context": "",
        "result": "",
        "route": ""
    })

    print("\nAI:", result["result"])
