var config = require('../config'),
    gulp = require('gulp');


gulp.task('watch', ['setwatch', 'browsersync'], function(callback) {
    // code uses watchify, so no need to watch from here
    gulp.watch(config.styles.watch, ['styles']);
    gulp.watch(config.assets.watch, ['assets']);

    callback();
});
