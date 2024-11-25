from firebase_admin import firestore
import datetime

db = firestore.client()

def save_player_history(player_id, name, email, score):
    try:
        doc_ref = db.collection("players").document(player_id)
        doc = doc_ref.get()

        if doc.exists:
            player_data = doc.to_dict()
            history = player_data.get("history", [])
        else:
            history = []

        # Thêm lịch sử mới
        history.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score
        })

        # Lưu lại vào Firestore
        doc_ref.set({
            "name": name,
            "email": email,
            "history": history
        })
        # print("Player history updated successfully!") # Debug

    except Exception as e:
        print(f"Error saving player history: {e}") # Debug
