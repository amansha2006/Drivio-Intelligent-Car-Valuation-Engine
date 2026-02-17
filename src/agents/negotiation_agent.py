# src/agents/negotiation_agent.py

def negotiation_advice(predicted_price: float) -> dict:
    """
    Provide buyer and seller negotiation advice based on predicted price.
    """

    buyer_low = int(predicted_price * 0.93)
    buyer_high = int(predicted_price * 0.96)
    seller_floor = int(predicted_price * 0.97)

    return {
        "buyer_advice": f"Try negotiating between ₹{buyer_low:,} and ₹{buyer_high:,}.",
        "seller_advice": f"Avoid selling below ₹{seller_floor:,}."
    }
