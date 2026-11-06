# Error Handling
Backend: HTTPException with detail; upload errors 400 with reason; auth 401/429; validation 422. Frontend: `ApiError` with status + body, per-view ErrorState with retry.
