rm -r './cpp/build'
cd './cpp'
mkdir "build"
cd ./build
cmake ..
make
cd ../..