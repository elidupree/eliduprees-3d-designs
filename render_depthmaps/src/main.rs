fn main() {
    eliduprees_3d_designs_lib::depthmap::depthmap_generation::run_specfile(
        &std::env::args().collect::<Vec<_>>()[1],
    );
}
