from backend import app

if __name__ == "__main__":
    #host 0.0.0.0 to access it on other devices on the same network, not suited for production
    app.run(debug=True, use_reloader=False, host = "0.0.0.0")