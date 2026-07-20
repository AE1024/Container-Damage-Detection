const BASE = '/api/v1'

async function request(method, path, body, isForm = false) {
  const token = localStorage.getItem('cg_token')
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!isForm) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  })

  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export const api = {
  /* AUTH */
  login:         (body) => request('POST', '/auth/login',       body),
  register:      (body) => request('POST', '/auth/register',    body),
  logout:        ()     => request('POST', '/auth/logout'),
  me:            ()     => request('GET',  '/auth/me'),
  updateProfile: (body) => request('PUT',  '/auth/me/profile',  body),

  /* CONTAINERS */
  analyze:          (form)   => request('POST',   '/containers/analyze',  form, true),
  registerContainer:(body)   => request('POST',   '/containers/register', body),
  listContainers:   (params) => {
    const q = new URLSearchParams()
    if (params?.date_from)      q.set('date_from',      params.date_from)
    if (params?.date_to)        q.set('date_to',        params.date_to)
    if (params?.limit)          q.set('limit',          params.limit)
    if (params?.container_no)   q.set('container_no',   params.container_no)
    if (params?.container_type) q.set('container_type', params.container_type)
    if (params?.company_name)   q.set('company_name',   params.company_name)
    return request('GET', `/containers/list?${q}`)
  },
  deleteContainer: (no) => request('DELETE', `/containers/${no}`),
}
