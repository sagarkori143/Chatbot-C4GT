import requests # type: ignore

# Define the base URL for the Flask API
base_url = 'http://127.0.0.1:5000/chatbot'

def test_main_menu():
    print("Testing main menu...")
    response = requests.post(base_url, json={"choice": "menu"})
    response_data = response.json()

    assert "question" in response_data, "Failed main menu test: 'question' key not found"
    assert response_data["options"] == ["Question 1", "Question 2", "Question 3"], "Failed main menu options test"
    print("Main menu test passed.")
    return response_data

def test_question_selection():
    print("Testing question selection...")
    response = requests.post(base_url, json={"choice": "Question 1"})
    response_data = response.json()
    print("Response from question selection:", response_data)
    
    if "question" in response_data:
        # If a sub-question is returned
        assert response_data["question"].startswith("Please choose an option from"), "Failed question selection test: Invalid question format"
        assert isinstance(response_data["options"], list), "Failed question selection test: 'options' should be a list"
    elif "answer" in response_data:
        # If an answer is returned
        assert isinstance(response_data["answer"], str), "Failed question selection test: 'answer' should be a string"
        assert response_data["options"] == ["Back to Main Menu"], "Failed question selection test: Invalid options for answer"
    else:
        assert False, "Failed question selection test: Neither 'question' nor 'answer' key found in response"

    print("Question selection test passed.")
    return response_data

if __name__ == "__main__":
    test_main_menu()
    test_question_selection()
    print("All tests passed.")
