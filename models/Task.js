
const mongoose = require("mongoose");

const taskSchema = new mongoose.Schema(
    {
        title: {
            type: String,
            required: true,
            trim: true,
            maxlength: 100
        },

        description: {
            type: String,
            trim: true,
            default: ""
        },

        priority: {
            type: String,
            enum: ["Low", "Medium", "High"],
            default: "Medium"
        },

        status: {
            type: String,
            enum: ["Pending", "In Progress", "Completed"],
            default: "Pending"
        },

        dueDate: {
            type: Date,
            default: null
        },

        userId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true,
            index: true
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model("Task", taskSchema);
