@Override
    public void handle(String target, Request baseRequest, HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException {
        String path = baseRequest.getPathInfo();
        int soff = 0, eoff;
        // We're handling this request
        baseRequest.setHandled(true);
        if(core.getLoginRequired()
            && request.getSession(true).getAttribute(LoginServlet.USERID_ATTRIB) == null){
            response.sendError(HttpStatus.UNAUTHORIZED_401);
            return;
        }
        if (path.charAt(0) == '/') soff = 1;
        eoff = path.indexOf('/', soff);
        if (soff < 0) {
            response.sendError(HttpStatus.NOT_FOUND_404);
            return;
        }
        String world = path.substring(soff, eoff);
        String uri = path.substring(eoff+1);
        // If faces directory, handle faces
        if (world.equals("faces")) {
            handleFace(response, uri);
            return;
        }
        // If markers directory, handle markers
        if (world.equals("_markers_")) {
            handleMarkers(response, uri);
            return;
        }

        DynmapWorld w = null;
        if (core.mapManager != null) {
            w = core.mapManager.getWorld(world);
        }
        // If world not found quit
        if (w == null) {
            response.setContentType("image/png");
            OutputStream os = response.getOutputStream();
            os.write(blankpng);
            return;
        }
        MapStorage store = w.getMapStorage();    // Get storage handler
        // Get tile reference, based on URI and world
        MapStorageTile tile = store.getTile(w, uri);
        if (tile == null) {
            response.setContentType("image/png");
            OutputStream os = response.getOutputStream();
            os.write(blankpng);
            return;
        }
        // Read tile
        TileRead tr = null;
        if (tile.getReadLock(5000)) {
            tr = tile.read();
            tile.releaseReadLock();
        }
        response.setHeader("Cache-Control", "max-age=0,must-revalidate");
        String etag;
        if (tr == null) {
        	etag = "\"" + blankpnghash + "\"";
        }
        else {
        	etag = "\"" + tr.hashCode + "\"";
        }
        response.setHeader("ETag", etag);
        String ifnullmatch = request.getHeader("If-None-Match");
        if ((ifnullmatch != null) && ifnullmatch.equals(etag)) {
            response.sendError(HttpStatus.NOT_MODIFIED_304);
        	return;
        }
        if (tr == null) {
            response.setContentType("image/png");
            response.setIntHeader("Content-Length", blankpng.length);
            OutputStream os = response.getOutputStream();
            os.write(blankpng);
            return;
        }
        // Got tile, package up for response
        response.setDateHeader("Last-Modified", tr.lastModified);
        response.setIntHeader("Content-Length", tr.image.length());
        if (tr.format == ImageEncoding.PNG) {
            response.setContentType("image/png");
        }
        else {
            response.setContentType("image/jpeg");
        }
        ServletOutputStream out = response.getOutputStream();
        out.write(tr.image.buffer(), 0, tr.image.length());
        out.flush();

    }