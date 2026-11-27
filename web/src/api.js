// Thin client for the Siteline API. The browser authenticates with the session cookie.
async function request(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    ...opts,
    headers: opts.body ? { 'content-type': 'application/json' } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body.error?.message || `Request failed (${res.status})`);
    err.status = res.status;
    err.code = body.error?.code;
    err.fields = body.error?.fields;
    throw err;
  }
  return body;
}

export const api = {
  get: (path) => request(path),
  post: (path, body = {}) => request(path, { method: 'POST', body }),
  del: (path) => request(path, { method: 'DELETE' }),
};
