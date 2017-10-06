#ifndef __SPRITE_H__
#define __SPRITE_H__

#include <Python.h>
#include "Config.h"

#include <memory>

//forward decl
class cppSimulatorImp;

#define SETATTR(data,attr) attr = data.at(#attr)

class Sprite {
public:
    Sprite(cppSimulatorImp* Engine,
        PyObject* canvas,
        Side side, pos_tup loc, double HP,
        double MP, double Speed,double Armor,
        double ATK,double ATKRange,double SightRange,
        double Bounty,double bountyEXP,
        double BAT,double AS):
        Engine(Engine),canvas(canvas),side(side),
        location(loc),HP(HP),MP(MP),MovementSpeed(Speed),
        BaseAttackTime(BAT),AttackSpeed(AS),Armor(Armor),
        Attack(ATK),AttackRange(ATKRange),SightRange(SightRange),
        Bounty(Bounty), bountyEXP(bountyEXP), LastAttackTime(-1),
        exp(0),_isDead(false),b_move(false), v_handle(NULL)
    {   
        _update_para();
    }

    Sprite() :LastAttackTime(-1),
        exp(0), _isDead(false), b_move(false), canvas(NULL), v_handle(NULL) {}

    virtual ~Sprite(){}

    inline void _update_para() {
        double AttackPerSecond = AttackSpeed * 0.01 / BaseAttackTime;
        AttackTime = 1 / AttackPerSecond;
    }

    virtual void step() = 0;
    virtual void draw() = 0;

    inline pos_tup pos_in_wnd() {
        return pos_tup(std::get<0>(location) * Config::game2window_scale * 0.5 + Config::windows_size * 0.5,
            std::get<1>(location) * Config::game2window_scale * 0.5 + Config::windows_size * 0.5);
    }

    void attack(Sprite* target);
    bool isAttacking();
    inline void set_move(pos_tup target) {
        b_move = true;
        move_target = target;
    }
    void move();
    bool damadged(double dmg);
    void dead();

    static double S2Sdistance(const Sprite& s1,const Sprite& s2);

    inline cppSimulatorImp* get_engine() { return Engine; }

    inline double get_AttackTime() { return AttackTime; }
    inline double get_Attack() { return Attack; }
    inline Side get_side() { return side; }
    inline double get_SightRange() { return SightRange; }
    inline pos_tup get_location() { return location; }
    inline bool isDead(){return _isDead;}

protected:
    cppSimulatorImp* Engine;
    PyObject* canvas;
    Side side;
    pos_tup location;
    double HP;
    double MP;
    double MovementSpeed;
    double BaseAttackTime;
    double AttackSpeed;
    double Armor;
    double Attack;
    double AttackRange;
    double SightRange;
    double Bounty;
    double bountyEXP;
    double LastAttackTime;
    double AttackTime;
    double exp;
    bool _isDead;
    bool b_move;
    PyObject* v_handle;
    pos_tup move_target;
};

#endif//__SPRITE_H__