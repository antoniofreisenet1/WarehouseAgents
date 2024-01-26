# Description: This file contains the implementation of the agent class and its methods. 
# This file is currently not operative, but it is intended to be used in the future for the implementation of the agent class and its methods.


class State:
    def __init__(self, position, description):
        self.position = position
        self.description = description


class Agent:
    def __init__(self, initial_state):
        self.state = initial_state
        self.beliefs = {"state":initial_state}
        self.desires = []
        self.intentions = []

    def update_beliefs(self, state, new_belief):
        self.beliefs[state] = new_belief

    def update_desires(self, new_desire):
        self.desires.append(new_desire)

    def generate_intentions(self):
        current_state = self.desires[0]
        if(self.desires):
            #Verificar que el deseo sea alcanzable
            current_desire = self.desires[0]
            if(current_desire == "go_to" and self.state.position == "A"):
                current_intention = current_desire
                self.intentions.append(current_intention) #test again later with structure: current_intention = current_desire and then self.intentions.append(current_intention)
                print(f"Intentions: {current_intention}")

            else:
                print("Desire not reachable")

        else:
            print("No desires")

    def execute_intentions(self):
        current_intention = self.intentions[0]
        current_state = self.beliefs["state"]
        if(self.intentions):
            if(current_intention == "go_to"):
                print("Going to B")
                self.state.position = "B"
                print(f"State: {self.state.position}")
                self.intentions.pop(0)
                self.desires.pop(0)
            else:
                print("Intention not executable")
        else:
            print("No intentions")


#Usage of the agent im a certain environment
            
initial_state = State("A", "Initial state")
            
Agent1 = Agent(initial_state)
Agent1.update_beliefs({"state": initial_state})
Agent1.update_desires("go_to")
Agent1.generate_intentions()
Agent1.execute_intentions()
