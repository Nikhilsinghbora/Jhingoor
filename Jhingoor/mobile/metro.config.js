const { getDefaultConfig } = require("expo/metro-config");

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

const upstreamEnhanceMiddleware = config.server?.enhanceMiddleware;

config.server = {
  ...config.server,
  /**
   * Opening http://localhost:PORT/ in a browser without ?platform=web often shows a blank
   * page. Redirect HTML navigations to the Metro web entry so the app (login) loads.
   */
  enhanceMiddleware: (middleware, server) => {
    const stack = upstreamEnhanceMiddleware ? upstreamEnhanceMiddleware(middleware, server) : middleware;
    return (req, res, next) => {
      const raw = req.url ?? "";
      const pathOnly = raw.split("?")[0] ?? "";
      const accept = req.headers.accept ?? "";
      const wantsHtml = accept.includes("text/html");
      const alreadyWeb = raw.includes("platform=web");

      if (wantsHtml && !alreadyWeb && (pathOnly === "/" || pathOnly === "/index.html")) {
        res.writeHead(302, { Location: "/?platform=web" });
        res.end();
        return;
      }
      return stack(req, res, next);
    };
  },
};

module.exports = config;
