import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// Define a new interface that extends Request
interface AuthRequest extends Request {
  user?: any; // or whatever type you expect for decoded JWT payload
}

const authMiddleware = (req: AuthRequest, res: Response, next: NextFunction) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).send({ message: 'Access denied. No token provided.' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any; // or specify the type you expect for decoded token
    req.user = decoded;
    next();
  } catch (error) {
    res.status(400).send({ message: 'Invalid token.' });
  }
};

export default authMiddleware;
