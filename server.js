
const express = require("express");
const mongoose = require("mongoose");
require("dotenv").config();
const {exec} = require("child_process");
const authRoutes = require("./routes/authRoutes");
const taskRoutes = require("./routes/taskRoutes");

const app = express();

// Middleware to read JSON data from requests
app.use(express.json());
app.use(express.static("public"));
app.use("/api/auth", authRoutes);
app.use("/api/tasks", taskRoutes);

// Test route
// app.get("/", (req, res) => {
//     res.send("TaskFlow server is running!");
// });

// Connect to MongoDB and start the server
mongoose
    .connect(process.env.MONGO_URI)
    .then(() => {
        console.log("MongoDB connected successfully!");

        const PORT = process.env.PORT || 3000;

        app.listen(PORT, () => {
            const url = `http://localhost:${PORT}`;

            console.log(`Server running on port ${PORT}`);
            console.log(`Opening TaskFlow in Chrome: ${url}`);

            exec(`start chrome "${url}"`, (error) => {
                if (error) {
                    console.log("Chrome could not be opened automatically.");
                    console.log(`Open this URL manually: ${url}`);
                }
            });
        });


    })
    .catch((error) => {
        console.error("MongoDB connection failed:", error.message);
        process.exit(1);
    });
