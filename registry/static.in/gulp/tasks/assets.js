var config = require('../config').assets,
    gulp = require('gulp');


gulp.task('assets', function() {
    gulp.src(config.src)
        .pipe(gulp.dest(config.dst));
});
