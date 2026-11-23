from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Inventory Management System</h1>
    <p>Welcome to our inventory dashboard!</p>
    <a href="/inventory">View Inventory</a>
    """


@app.route("/inventory")
def inventory():
    return """
    <h1>Inventory List</h1>
    <p>Welcome to the inventory page.</p>

    <ul>
        <li>Laptop - 20 units</li>
        <li>Keyboard - 15 units</li>
        <li>Mouse - 30 units</li>
    </ul>

    <a href="/">Back to Home</a>
    """


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

