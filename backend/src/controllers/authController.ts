import { AppContext } from '../app-context';
import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { runQuery, executeQuery } from '../database/sqlite-proxy.js';

import { components } from '../routes/schema.js';


// Function to hash password using bcrypt
const hashPassword = (password: string): Promise<string> => {
    return bcrypt.hash(password, 10); // Using 10 salt rounds
};

// Function to compare passwords using bcrypt
const comparePasswords = (password: string, hashedPassword: string): Promise<boolean> => {
    return bcrypt.compare(password, hashedPassword);
};

// Function to generate authentication token
const generateAuthToken = (user: { username: string }) => {
    return jwt.sign(user, process.env.JWT_SECRET!, { expiresIn: '1h' });
};


// Function to sign up a user
export const signUp = async (req: Request, res: Response) => {
    let response: components["schemas"]["SignupResponse"] = {};;
    try {
        const appContext: AppContext | undefined = req.appContext;
        const reqData: components["schemas"]["SignupRequest"] = req.body;

        const {username, password, firstName, lastName} = reqData;

        const hashedPassword = await hashPassword(password);
        const query = `INSERT INTO 'users' (username, password, firstName, lastName, role) VALUES (?, ?, ?, ?, ?)`;
        await runQuery(query, [username, hashedPassword, firstName, lastName, 'user']);
        response.message = 'User created successfully';
        res.status(201).send(response);
    } catch (error) {
        response.message = 'Error signing up';
        console.error("Error signing up:", error);
        res.status(400).send(response);
    }
};

// Function to sign in a user
export const signIn = async (req: Request, res: Response) => {
    let response: components["schemas"]["SigninResponse"] = {};;
    try {
        const appContext: AppContext | undefined = req.appContext;
        const reqData: components["schemas"]["SigninRequest"] = req.body;

        const { username, password } = reqData;

        const query = `SELECT * FROM 'users' WHERE username = ?`;
        const rows = await executeQuery(query, [username]);

        if (rows.length === 1 && await bcrypt.compare(password, rows[0].password)) {
            const token = generateAuthToken({ username });
            response.message = 'User signed in successfully';
            response.username = rows[0].username;
            response.firstName = rows[0].firstName;
            response.lastName = rows[0].lastName;
            response.role = rows[0].role;
            response.token = token;
            res.status(200).send(response);
        } else {
            response.message = 'Invalid username or password';
            res.status(401).send(response);
        }
    } catch (error) {
        response.message = 'Error signing in';
        console.error("Error signing in:", error);
        res.status(400).send(response);
    }
};

// Function to change password
export const changePassword = async (req: Request, res: Response) => {
    let response: components["schemas"]["ChangePasswordResponse"] = {};;
    try {
        const reqData: components["schemas"]["ChangePasswordRequest"] = req.body;
        const { username, oldPassword, newPassword } = req.body;
        const query1 = `SELECT * FROM 'users' WHERE username = ?`;
        const rows = await executeQuery(query1, [username]);

        if (rows.length === 1 && await bcrypt.compare(oldPassword, rows[0].password)) {
            try {
                const hashedPassword = await hashPassword(newPassword);
                const query2 = `UPDATE 'users' SET password = ? WHERE username = ?`;
                await runQuery(query2, [hashedPassword, username]);
                response.message = 'Password changed successfully';
                res.status(200).send(response);
            } catch (error) {
                response.message = 'Error changing password';
                console.error("Error changing password:", error);
                res.status(400).send(response);
            }
        } else {
            res.status(401).send('Invalid password');
        }
    } catch (error) {
        response.message = 'Error changing password';
        console.error("Error changing password:", error);
        res.status(400).send(response.message);
    }
};