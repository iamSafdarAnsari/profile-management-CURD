const API_URL = window.location.origin + '/api'; // works when backend serves frontend

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function clearToken() {
  localStorage.removeItem('token');
}

// ---------- Register ----------
function submitRegister(formSelector, successCb, errorCb) {
  const formData = $(formSelector).serializeArray();
  let payload = {};
  formData.forEach(f => payload[f.name] = f.value);

  $.ajax({
    url: API_URL + '/signup',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(payload),
    success: successCb,
    error: (xhr) => {
      const err = xhr && xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Server error';
      errorCb(err);
    }
  });
}

// ---------- Login ----------
function submitLogin(formSelector, successCb, errorCb) {
  const formData = $(formSelector).serializeArray();
  let payload = {};
  formData.forEach(f => payload[f.name] = f.value);

  $.ajax({
    url: API_URL + '/login',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(payload),
    success: (res) => {
      setToken(res.token);
      successCb(res);
    },
    error: (xhr) => {
      const err = xhr && xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Server error';
      errorCb(err);
    }
  });
}

// ---------- Fetch Profile ----------
function fetchProfile(successCb, errorCb) {
  $.ajax({
    url: API_URL + '/profile',
    type: 'GET',
    headers: { 'Authorization': getToken() },
    success: successCb,
    error: (xhr) => {
      const err = xhr && xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Server error';
      errorCb(err);
    }
  });
}

// ---------- Update Profile ----------
function updateProfile(payload, successCb, errorCb) {
  $.ajax({
    url: API_URL + '/profile',
    type: 'PUT',
    headers: { 'Authorization': getToken() },
    contentType: 'application/json',
    data: JSON.stringify(payload),
    success: successCb,
    error: (xhr) => {
      const err = xhr && xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Server error';
      errorCb(err);
    }
  });
}
