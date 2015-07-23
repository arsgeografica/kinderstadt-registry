var autoprefixer = require('gulp-autoprefixer'),
    config = require('../config').styles,
    gulp = require('gulp'),
    less = require('gulp-less'),
    minify = require('gulp-minify-css'),
    plumber = require('gulp-plumber'),
    sourcemaps = require('gulp-sourcemaps');


gulp.task('styles', function(callback) {
    gulp.src(config.src, { base: config.srcBase })
        .pipe(plumber())
        .pipe(sourcemaps.init())
        .pipe(less(config.less))
        // .pipe(sourcemaps.write()) // Write and reload sourcemap for autoprefixer
        // .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(autoprefixer())
        .pipe(minify(config.minify))
        // .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(config.dst));

    callback();
});
