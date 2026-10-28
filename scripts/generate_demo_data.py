import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sample conversational vocabularies
GREETINGS = ["Hey", "Hi there", "Good morning", "Hello", "Hey, quick question"]
CASUAL_MESSAGES = [
    "Did you see the latest update?",
    "Let me know when you get a chance to review the document.",
    "Sounds great, thanks!",
    "Are you free for a quick call this afternoon?",
    "I just sent over the revised presentation.",
    "Can you check the pull request when you have time?",
    "What do you think about the proposed timeline?",
    "No worries at all, take your time.",
    "Let's catch up tomorrow morning.",
    "Got it, will take a look shortly.",
    "Are we still on for our sync at 3 PM?",
    "Here is the link: https://docs.example.com/project-brief",
    "Please let me know if you need anything else from my side.",
    "Awesome, talk to you soon! 👍",
    "Where should we meet for lunch?",
    "Do you have the latest figures from yesterday?",
    "Happy Friday! Any plans for the weekend?",
    "Hey! Just following up on this.",
    "Can you ping me when you're back at your desk?",
    "I will be online in 10 minutes."
]

RESPONSES = [
    "Hey! Yes, just looked at it. Looks good to go.",
    "Sure, let's do 3:30 PM instead.",
    "Thanks for sending, I'll review it by end of day.",
    "Yes, absolutely. Joining the room now.",
    "Sounds like a plan! Let me confirm with the team.",
    "Reviewed and approved! Great job on this.",
    "Sorry for the delay, was in back-to-back meetings. What's up?",
    "Got it, will send you the numbers right away.",
    "Yes, still on! See you soon.",
    "Checking it out right now 👍"
]


def generate_single_conversation(
    conv_id: str,
    sender_name: str,
    recipient_name: str,
    start_dt: datetime,
    responsiveness: float = 0.75,  # Probability of replying
    avg_delay_mins: float = 45.0,
    turns_count: int = 15
) -> dict:
    current_time = start_dt
    messages = []
    msg_id = 1

    for turn_idx in range(turns_count):
        # Sender sends 1 to 3 messages
        sender_burst = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        sender_messages = []
        for b in range(sender_burst):
            text = random.choice(CASUAL_MESSAGES)
            # Add some emojis occasionally
            if random.random() < 0.25:
                text += " " + random.choice(["😊", "👍", "🙏", "🙌", "✨"])
            sender_msg = {
                "id": f"msg_{conv_id}_{msg_id}",
                "timestamp": current_time.isoformat(),
                "sender": sender_name,
                "text": text,
                "is_media": False,
                "is_system": False
            }
            messages.append(sender_msg)
            sender_messages.append(sender_msg)
            msg_id += 1
            current_time += timedelta(minutes=random.randint(1, 5))

        # Does recipient reply?
        will_reply = random.random() < responsiveness
        if will_reply:
            # Recipient reply delay (log-normal distribution)
            delay = max(2.0, random.gauss(avg_delay_mins, avg_delay_mins * 0.4))
            current_time += timedelta(minutes=delay)
            recip_burst = random.choices([1, 2], weights=[0.8, 0.2])[0]
            for rb in range(recip_burst):
                r_text = random.choice(RESPONSES)
                if random.random() < 0.2:
                    r_text += " " + random.choice(["👌", "🎉", "🔥"])
                messages.append({
                    "id": f"msg_{conv_id}_{msg_id}",
                    "timestamp": current_time.isoformat(),
                    "sender": recipient_name,
                    "text": r_text,
                    "is_media": False,
                    "is_system": False
                })
                msg_id += 1
                current_time += timedelta(minutes=random.randint(1, 4))
        else:
            # Conversation goes cold or sender restarts conversation later
            gap_hours = random.randint(12, 48)
            current_time += timedelta(hours=gap_hours)

    return {
        "conversation_id": conv_id,
        "sender": sender_name,
        "recipient": recipient_name,
        "messages": messages
    }


def generate_benchmark_dataset():
    """Generates 40 realistic multi-turn conversations with diverse dynamics."""
    conversations = []
    pairs = [
        ("Alex Chen", "Sarah Miller", 0.85, 20.0),    # Highly responsive colleague
        ("Jordan Taylor", "Morgan Lee", 0.65, 60.0),  # Moderately responsive
        ("David Kim", "Emma Watson", 0.40, 180.0),    # Slow / low responsiveness
        ("Priya Sharma", "Rahul Patel", 0.90, 15.0),  # Close collaboration
        ("Marcus Vance", "Elena Rostova", 0.50, 90.0) # Variable response rate
    ]

    base_time = datetime(2024, 3, 1, 9, 0, 0)

    for i in range(40):
        pair = pairs[i % len(pairs)]
        start_time = base_time + timedelta(days=i * 2, hours=random.randint(0, 8))
        conv = generate_single_conversation(
            conv_id=f"conv_{i+1:03d}",
            sender_name=pair[0],
            recipient_name=pair[1],
            start_dt=start_time,
            responsiveness=pair[2],
            avg_delay_mins=pair[3],
            turns_count=random.randint(10, 20)
        )
        conversations.append(conv)

    # Save benchmark corpus
    benchmark_path = DATA_DIR / "benchmark_conversations.json"
    with open(benchmark_path, "w", encoding="utf-8") as f:
        json.dump(conversations, f, indent=2)
    print(f"Generated benchmark corpus: {benchmark_path} ({len(conversations)} conversations)")

    # Save sample WhatsApp TXT export
    sample_conv = conversations[0]
    sample_txt_path = DATA_DIR / "sample_whatsapp.txt"
    with open(sample_txt_path, "w", encoding="utf-8") as f:
        f.write("15/01/2024, 09:00 - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them.\n")
        for m in sample_conv["messages"][:30]:
            dt = datetime.fromisoformat(m["timestamp"])
            date_part = dt.strftime("%d/%m/%Y")
            time_part = dt.strftime("%I:%M %p").lstrip("0")
            f.write(f"{date_part}, {time_part} - {m['sender']}: {m['text']}\n")
    print(f"Generated sample WhatsApp export: {sample_txt_path}")

    # Save sample CSV
    sample_csv_path = DATA_DIR / "sample_chat.csv"
    with open(sample_csv_path, "w", encoding="utf-8") as f:
        f.write("timestamp,sender,text\n")
        for m in conversations[1]["messages"][:30]:
            clean_text = m["text"].replace('"', '""')
            f.write(f'"{m["timestamp"]}","{m["sender"]}","{clean_text}"\n')
    print(f"Generated sample CSV export: {sample_csv_path}")

    # Save sample JSON
    sample_json_path = DATA_DIR / "sample_chat.json"
    with open(sample_json_path, "w", encoding="utf-8") as f:
        json.dump(conversations[2]["messages"][:30], f, indent=2)
    print(f"Generated sample JSON export: {sample_json_path}")


if __name__ == "__main__":
    generate_benchmark_dataset()
