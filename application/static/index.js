! function() {
    "use strict";
    ! function() {
        if ("requestAnimationFrame" in window && !/Mobile|Android/.test(navigator.userAgent)) {
            var e = document.querySelectorAll("[data-bss-parallax]");
            if (e.length) {
                var t, n = [];
                window.addEventListener("scroll", a), window.addEventListener("resize", a), a()
            }
        }

        function a() {
            n.length = 0;
            for (var a = 0; a < e.length; a++) {
                var r = e[a].getBoundingClientRect(),
                    o = parseFloat(e[a].getAttribute("data-bss-parallax-speed"), 10) || .5;
                r.bottom > 0 && r.top < window.innerHeight && n.push({
                    speed: o,
                    node: e[a]
                })
            }
            cancelAnimationFrame(t), n.length && (t = requestAnimationFrame(i))
        }

        function i() {
            for (var e = 0; e < n.length; e++) {
                var t = n[e].node,
                    a = n[e].speed;
                t.style.transform = "translate3d(0, " + -window.scrollY * a + "px, 0)"
            }
        }
    }()
}(),
function(e) {
    e(".vInputImage").change((function(t) {
        let n = t.target.files[0];
        if (n) {
            let a = e(this).parent(),
                i = new FileReader;
            i.onload = function() {
                t.target.parentNode.style.backgroundImage = `url('${i.result}')`
            }, i.readAsDataURL(n), a.find("button").removeClass("d-none"), a.trigger("ip.img.change", [n, a.attr("input-data-index")])
        }
    })), e(".vClearPreviewImage").click((function(t) {
        let n = e(this).parent();
        t.currentTarget.classList.add("d-none"), n.css("background-image", "url('/input_image_preview/upload_image.png')"), n.find("input").val(null), n.trigger("ip.img.clear", [n.attr("input-data-index")])
    }))
}(jQuery), document.querySelectorAll("[data-bss-baguettebox]").length > 0 && baguetteBox.run("[data-bss-baguettebox]", {
    animation: "slideIn"
});