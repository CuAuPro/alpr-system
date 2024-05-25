import Express from 'express';
import { signUp, signIn, changePassword } from '../controllers/authController.js';

export default class AuthRoutes {
  public router: Express.Router;
  //private upload: multer.Multer;

  constructor() {

    this.router = Express.Router();
    this.router.use(
      (
        req: Express.Request,
        res: Express.Response,
        next: Express.NextFunction
      ) => {
        console.log("/auth, Time: ", Date.now());
        next();
      }
    );


    // Sign-up route
    this.router.post('/signup', signUp);

    // Sign-in route
    this.router.post('/signin', signIn);

    // Password reset route
    this.router.post('/change-password', changePassword);

  }
}

