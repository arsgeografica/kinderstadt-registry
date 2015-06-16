var config = require('../config').clean,
    del = require('del'),
    gulp = require('gulp'),
    gutil = require('gulp-util');


gulp.task('clean', function(callback) {
    del(config.glob, config.options, function(err, files) {
        if(err) {
            callback(err);
        }

        gutil.log(gutil.colors.bgGreen('Deleted ' + files.length + ' files.'));

        callback();
    });
});
