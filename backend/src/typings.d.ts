import { AppContext } from "./app-context.js";


declare global {
    namespace Express {
      interface Request {
        appContext?: AppContext;
      }
    }
  }