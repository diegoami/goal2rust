// The translated routines as port functions fn(mem, variant), included by py.rs. `PORTS` maps each to its address.
routine!(r_0791_2b51, crate::geometry::slot_is_on_ball_side);
routine!(r_0791_2974, crate::geometry::side);
routine!(r_0791_2be5, crate::geometry::direction);
routine!(r_0791_045d, crate::geometry::keeper);
routine!(r_0791_26d7, crate::geometry::player_effective_tactic);
routine!(r_0791_2c29, crate::geometry::slot_is_idle_ball_slot);
routine!(r_0791_2cec, crate::geometry::player_at_ball);

/// T01's falsifiers (geometry::MUTANT): 0 none, 1 or 2 a deliberate difference.
#[pyfunction]
fn set_mutant(n: u32) {
    crate::geometry::MUTANT.store(n, std::sync::atomic::Ordering::Relaxed);
}

fn register_routines(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(set_mutant, m)?)?;
    let ports = PyDict::new(m.py());
    for (addr, f) in [
        ("0791:2B51", wrap_pyfunction!(r_0791_2b51, m)?),
        ("0791:2974", wrap_pyfunction!(r_0791_2974, m)?),
        ("0791:2BE5", wrap_pyfunction!(r_0791_2be5, m)?),
        ("0791:045D", wrap_pyfunction!(r_0791_045d, m)?),
        ("0791:26D7", wrap_pyfunction!(r_0791_26d7, m)?),
        ("0791:2C29", wrap_pyfunction!(r_0791_2c29, m)?),
        ("0791:2CEC", wrap_pyfunction!(r_0791_2cec, m)?),
    ] {
        m.add_function(f.clone())?;
        ports.set_item(addr, f)?;
    }
    m.add("PORTS", ports)?;
    Ok(())
}
