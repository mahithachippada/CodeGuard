var user = "admin";                 // WARNING: use of var
var password = "admin123";          // CRITICAL: hardcoded secret

function login(u, p) {              // INFO: no documentation
    if (u == "admin") {
        eval("console.log('Hi')");  // CRITICAL: eval usage
    }

    console.log("Debug login");     // INFO: debug log
}

login(user, password);
