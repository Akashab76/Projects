
const jwt = require("jsonwebtoken");

const authMiddleware = (req, res, next) => {
    try {
        // Read the token from the Authorization header
        const authHeader = req.headers.authorization;

        if (!authHeader || !authHeader.startsWith("Bearer ")) {
            return res.status(401).json({
                message: "Access denied. Please log in."
            });
        }

        // Extract the token
        const token = authHeader.split(" ")[1];

        // Verify the token using our secret
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        // Attach the authenticated user's ID to the request
        req.userId = decoded.userId;

        // Continue to the requested route
        next();

    } catch (error) {
        return res.status(401).json({
            message: "Invalid or expired token. Please log in again."
        });
    }
};

module.exports = authMiddleware;
