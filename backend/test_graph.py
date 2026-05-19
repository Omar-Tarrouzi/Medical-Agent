import asyncio
from app.graph import graph
from langgraph.types import Command

async def test_flow():
    config = {"configurable": {"thread_id": "test-12345"}}
    
    initial_state = {
        "initial_complaint": "J'ai mal a la tete depuis 3 jours.",
        "question_count": 0,
        "patient_qa": [],
        "messages": [],
    }

    print("Starting graph...")
    try:
        graph.invoke(initial_state, config)
    except Exception as e:
        print(f"Exception during start: {e}")

    # Answer questions in a loop
    for i in range(1, 7):
        state = graph.get_state(config)
        print(f"DEBUG: Current question_count in state = {state.values.get('question_count')}")
        interrupts = state.tasks[0].interrupts if state.tasks else []
        
        if not interrupts:
            print(f"No interrupts at step {i}. Graph finished or routed to supervisor.")
            print(f"Final state: {state.values.get('question_count')} questions")
            print(f"Synthesis: {state.values.get('diagnostic_summary')}")
            break
            
        interrupt_val = interrupts[0].value
        print(f"\n--- STEP {i} ---")
        print(f"Interrupt: {interrupt_val['type']}")
        
        if interrupt_val['type'] == 'patient_question':
            print(f"AI Asks: {interrupt_val['question']}")
            answer = f"Ma réponse à la question {i} est blabla."
            print(f"Patient Answers: {answer}")
            
            try:
                graph.invoke(Command(resume=answer), config)
            except Exception as e:
                import traceback
                print(f"CRASH during resume {i}:")
                traceback.print_exc()
                break
        elif interrupt_val['type'] == 'physician_review':
            print("Reached physician review!")
            break

if __name__ == "__main__":
    asyncio.run(test_flow())
