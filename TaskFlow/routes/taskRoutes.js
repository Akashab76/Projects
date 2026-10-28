
const express = require("express");
const mongoose = require("mongoose");
const Task = require("../models/Task");
const authMiddleware = require("../middleware/authMiddleware");

const router = express.Router();

// Protect every route in this file
router.use(authMiddleware);

// CREATE a task
router.post("/", async (req, res) => {
    try {
        const { title, description, priority, status, dueDate } = req.body;

        if (!title || typeof title !== "string" || !title.trim()) {
            return res.status(400).json({
                message: "Task title is required"
            });
        }

        const task = await Task.create({
            title: title.trim(),
            description,
            priority,
            status,
            dueDate: dueDate || null,
            userId: req.userId
        });

        res.status(201).json({
            message: "Task created successfully",
            task
        });
    } catch (error) {
        if (error.name === "ValidationError" || error.name === "CastError") {
            return res.status(400).json({
                message: "Invalid task data"
            });
        }

        console.error("Create task error:", error.message);
        res.status(500).json({ message: "Server error" });
    }
});


// READ all tasks belonging to the logged-in user
router.get("/", async (req, res) => {
    try {
        const tasks = await Task.find({
            userId: req.userId
        }).sort({ createdAt: -1 });

        res.status(200).json({ tasks });
    } catch (error) {
        console.error("Fetch tasks error:", error.message);
        res.status(500).json({ message: "Server error" });
    }
});


// UPDATE a task belonging to the logged-in user
router.put("/:id", async (req, res) => {
    try {
        const { id } = req.params;

        if (!mongoose.isValidObjectId(id)) {
            return res.status(400).json({
                message: "Invalid task ID"
            });
        }

        const allowedFields = [
            "title",
            "description",
            "priority",
            "status",
            "dueDate"
        ];

        const updates = {};

        for (const field of allowedFields) {
            if (req.body[field] !== undefined) {
                updates[field] = req.body[field];
            }
        }

        if (Object.keys(updates).length === 0) {
            return res.status(400).json({
                message: "No valid fields provided for update"
            });
        }

        if (
            updates.title !== undefined &&
            (typeof updates.title !== "string" ||
             !updates.title.trim())
        ) {
            return res.status(400).json({
                message: "Title cannot be empty"
            });
        }

        if (updates.title !== undefined) {
            updates.title = updates.title.trim();
        }

        if (updates.dueDate === "") {
            updates.dueDate = null;
        }

        const task = await Task.findOneAndUpdate(
            { _id: id, userId: req.userId },
            { $set: updates },
            { new: true, runValidators: true }
        );

        if (!task) {
            return res.status(404).json({
                message: "Task not found"
            });
        }

        res.status(200).json({
            message: "Task updated successfully",
            task
        });
    } catch (error) {
        if (error.name === "ValidationError" || error.name === "CastError") {
            return res.status(400).json({
                message: "Invalid task data"
            });
        }

        console.error("Update task error:", error.message);
        res.status(500).json({ message: "Server error" });
    }
});


// DELETE a task belonging to the logged-in user
router.delete("/:id", async (req, res) => {
    try {
        const { id } = req.params;

        if (!mongoose.isValidObjectId(id)) {
            return res.status(400).json({
                message: "Invalid task ID"
            });
        }

        const task = await Task.findOneAndDelete({
            _id: id,
            userId: req.userId
        });

        if (!task) {
            return res.status(404).json({
                message: "Task not found"
            });
        }

        res.status(200).json({
            message: "Task deleted successfully"
        });
    } catch (error) {
        console.error("Delete task error:", error.message);
        res.status(500).json({ message: "Server error" });
    }
});

module.exports = router;
