import 'react-dom'

console.log("Loaded react-dom");

console.log("Webpack works");

(function () {
    $(document).ready(function () {
        userController.init(configConstants);
        videoController.init(configConstants);
        uploadController.init(configConstants);
    });
}());
