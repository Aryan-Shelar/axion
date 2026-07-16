# Axion v2.0 security model

Profile data remains in ignored local storage. Sensitive values use Windows DPAPI; Axion refuses to silently store them as plaintext when DPAPI is unavailable. The autofill bridge binds only to `127.0.0.1`, creates a random token per start, validates requests, and returns only requested fields. Sites are denied unless allowlisted.

Forms are never submitted automatically. Passwords, OTP/verification codes, CVV/card/payment/bank fields, security answers, and digital signatures are blocked. Aadhaar, PAN, date of birth, phone, and address require one-operation approval. Logs contain domains, field names, and status only—not values. Browsers prohibit silently setting file inputs, so document paths are suggestions and users choose files manually.
