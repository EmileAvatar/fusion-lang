Youtube: https://www.youtube.com/watch?v=gKKZvnRYzFI
Title: Why I Don't Like Rust


--- summary ---
## What the speaker likes—and what he objects to

- The speaker values Rust’s safety and error checking, and says the borrow checker has not been a problem for him; his objection is not that Rust is unsafe or that its borrowing rules are difficult.  
- His main criticism is that Rust’s idioms conflict with his preferences: he favors index-based loops, explicit types and control flow, procedural code, and simpler abstractions, while he sees Rust as encouraging iterators, inferred types, traits, macros, and chained function calls.    
- This is a preference-based critique, not a claim that Rust is a bad language; the speaker says it works well for people who like its style.    

## Tagged unions, derives, and generated code

- Rust’s `enum` can represent alternatives that carry different data, which the speaker calls a tagged union; he contrasts this with a traditional integer enum, where each named value represents an integer constant.      
- In his example, a result type contains either page content or an HTTP error, and that error may itself be represented by another tagged union; he finds this nesting and the required pattern matching harder to follow than using integer error codes and explicit conditionals.        
- The speaker objects that Rust requires derives to add capabilities such as printing or comparing some types, because derive macros generate implementation code at compile time; he contrasts this with Zig, where he says his example types can be printed and compared directly.      
- He argues that repeatedly generating implementations for result, optional, and other types can add compile-time work; his estimate of thousands of generated lines is an illustrative extrapolation, not a measured result presented in the video.    

## Iterators, type inference, and readability

- The speaker’s directory-walking example chains iterator operations such as filtering and mapping, which he finds difficult to reason about because the intermediate types and error handling are obscured by the chain.      
- When he tries to spell out the iterator types, he says some are difficult or impossible to name directly because they are compiler-generated implementation types; this reinforces his preference for breaking work into explicit steps with visible types.      
- His alternative uses loops, named intermediate values, explicit type annotations, and separate error handling; he considers this easier to inspect and debug, even though he recognizes Rust users may prefer idiomatic iterator-based code.        

## Debug-mode stack overflow and performance concerns

- The speaker reports that a large constant array caused a stack overflow in his Rust debug-mode test, while the same example ran in release mode; he expected the constant not to consume stack space in a way that caused this failure.      
- He compares the test with Zig and argues that because both languages use LLVM, the difference points to Rust’s handling rather than LLVM alone; this is his interpretation of the comparison.    
- In a chess move-generator benchmark, he reports that reorganizing code into methods on a struct made it about 40% faster, and criticizes the size of that difference between code organizations.      
- Overall, his conclusion is that Rust’s abstractions and conventions make it unpleasant for his preferred coding style, while its safety features are not the source of his dissatisfaction.


--- transcribe ---

 Hi everyone. This video is why I don't like Rust. So, first I want to say that if you like Rust, that's fine. Some people like Haskell, some people like Pascal, some people like Python, some people like C++. It depends on the person. It's just my opinion and we shouldn't make fun or make a war between each other. So C++ developers are fighting against Rust developers. We're all programmers. Why are we fighting? It's just a preference. So firstly, I'll

say what I do like about Rust. First of all is safety. It's a lot safer than say C++ or C. Uh it has it it forces you to check errors. The borrow checker I'm completely fine with. I've never actually had problems with the borrow checker, which is probably the most common complaint I guess for people trying Rust is they don't understand the borrow checker. It's not that hard, but I basically code that way anyway. Why would you use two mutable references to

a thing? I've never really had problems with it, so it's not a complaint of mine. I like the basic syntax of semicolons and curly braces. It's similar to C, C++, C. Uh I don't like the really advanced syntax because I can't really read that, but we'll get into that later. And as I've tried to make compilers myself, I know how ridiculously difficult it is. And the Rust compiler is probably the hardest of all of them. It is insane how difficult

it is to make this kind of thing. Not only do you have to track every declared variable, but you have to track when they're created and when they are destroyed and when you create another reference to them and then delete the old one. This is a ridiculous amount of work, which I'll probably make a future video on because it's insane how difficult it is to make something like this. Now, let's get into why I don't like the language. So, my number one

problem is it forces you into a certain style of programming. Here's my general style that I prefer. Number one is I prefer index based loops over iterators. It's just a preference I have. I prefer explicit code over hidden magic. I prefer simplicity over complicated abstraction. I prefer languages that don't require you to learn hundreds of different features just to be able to use them at all. I prefer specifying types and hate inferred types. And I prefer procedural programming. So what's

the problem? I have just described the opposite of Rust. In Rust, you basically are forced to use iterators. Most of the time, a lot of the code is based on hidden magic. It's based on macros like derive macros. It's the based on the compiler writing code for you that's generated at compile time. Generally, a lot of things are hidden from you. Rust is based around complicated abstractions, things like tagged unions, traits, macros. You have to learn

hundreds of features just to be able to use Rust. Cargo.L. How do you use dependencies? How do you use a global variable? What's an unsafe block? How do you put stuff on the heap? How many different string types are there? Rust uses inferred types most of the time and almost forces you to use them. In some situations, you literally can't even do it. Rust uses the OOP style of strrus with interfaces. They're not called

interfaces, but that's what they are. My main language is actually C#, and I've literally never seen the point of ever writing an interface. I don't bother with it. So I don't see the point in ever using traits either. I don't see why you would do this. And then it's based around functional programming and not necessarily just not having global variables and having functions that are have no side effects, but it also uses what I call function callion where you call about five or six

different functions in a row and chain them. So my main problem is the way I actually light a code I can't do in Rust. the the language will actively fight me and everyone who actually codes in Rust will say, "Oh, you're writing it wrong. Why are you writing it like this?" And the comment section will probably be full of this. Oh, you're writing Rust wrong. I know that's my problem with the language. I can't write how I want. Thanks for proving my point.

So, let me give an example of some of the hidden magic inside Rust. So, Rust has these things called enums. So, they're called enums, but I have no idea why they're called enums because enums are enumerated values, and they're basically just automated constants for integers. That's all they are. Can an integer hold a generic value like a string or another enum? Not really. It's an integer. It's enum stands for enumerated values. They are constants for integers.

Rust doesn't have enums. They have tagged unions. It is not an enum. It's a tagged union. Why are you calling it an enum? Here's an example of some code where we're just simulating opening a website and we're going to use enums or tags unions. So, here's a very simple example. So, we're basically simulating opening a web page and getting an error code. We're just going to open this page with the URL this page. Of course, we're using inferred types all the time

because that's apparently what you're supposed to do in Rust, even though I hate using inferred types. Doesn't matter. Okay, so we're going to try to open this page. We get to open page. And this returns a result of a string or an HTTP error. An HTTP error is this thing. And then we have this nonsense at the top. What is this? So, for some reason, an enum type isn't considered part of the base language. you have to add stuff

to it in order to use them. So if you want to print them, you have to put this thing derive for some reason. And this will basically generate some code for you at compile time for some reason. Um I don't know why this is the case cuz enums are pretty important. They're used everywhere in Rust. They're not actually enums, but anyway, they're used everywhere in Rust. They're even basically if you look at result type. What's result type? Let's have a look.

Oh, it's an enam and it has all these derives on it. Oh, okay. So, you have basically your whole language is based around tagged unions, but you have to do this to derive. So, you can even print them or compare them or like like the basic functionality of an enum should be can I print it? Can I compare it? What else do I even need? But apparently no. Like you can use match case. So you can use a match case

without deriving anything from it. But everything else you can't print it, you can't compare it. You mean just like why do I need to do this just to print an enum? If I did this in zig. All right, let's do this in zig. So we've done exactly the same thing and you you can just Okay, you set it to this. Okay, we can compare it and we can print it innately. Why do I need to have the compiler generate stuff when it should

be inbuilt in the language? It's like if I create an integer like this, you know what I can do with this number? I can compare it. Look at this. Equals 10. Oh, look. Do I need to derive something from this? Oh, should I should I do this? Derive something like this. No, because no one would use this language if you had to do that for every integer you created. But for some reason, people tolerate it for

enums. Uhhuh. Let me compare it. let me print it by default because that's what you do with it anyway. I mean basically every enum is going to have debug drive debug dive debug like oh are you seeing my frustration yet? Right. And then okay so we have we're basically just going to see we're just going to simulate stuff. So if it's example we're just going to say page content here return a string and yeah just to confuse you. Yeah. So

result type is an enum itself a tagged union. So result type is a tagged union and we're putting in our own tagged union into another tagged union if that makes sense. So we're going to have a tagged union with a tag union inside the tagged union and then inside that we're going to have another tagged union. Okay, we're going to So we're going to use this tagged union to use the error code of this tagged union within this side inside this tagged union. This is just overengineered

unnecessarily complicated. And then I have to use match case. Let me show you how I would actually want to code this. All right. So then we run it and it just says trying to open page example.com admin error 401 unauthorized. All right. All right. So I've created an actual enum. What an actual enum is it's a constant that represents a number. They can't hold strings. They can't hold other tagged unions. So I've just created this for myself. given them

values and then have this HTTP result two string so I can print them. That's all I need to do. And then I have this page data just to hold the data and the code. Uh then I just pass I just return that. So I could make it an optional like this. But what's an optional? Oh, it's another tag union. Okay. Do I really want to use tag unions everywhere? It's tag unions all the way down. Uh no, I I I don't I'm just going

to give it not any value. just not any and then see if it's not any or just use the error code and then I just have an i32 error code which is it again represents this and then we just literally just set the content if it's that or we set the code and then just return page data. That's pretty much it. And then we just print it. I don't have to use a match case. I can compare it. Look, I can compare it by default. Oh, I

didn't used to have to use derive and have my have the compiler generate loads of code for me. For some reason, I needed to do this when I I just want to compare it. You can't like why can't I just compare it here? I can also print it using HTTP HTTP result to string and it prints. And this basically prints out exactly the same thing as before. It's just a lot less difficult to make for me. And I know I don't need to

understand there's a tag union inside a tag union with this. I don't have to use a match case. I can simply just say if it's that then just print it. This is just easier for me. But apparently, oh, I'm not following the style guide. You should use tagged union. I don't want to use tag union. Sorry. It's over complicated. I don't need to. So, just to drive my point home, if I wanted to

create the exact same thing in in Zigg as we did in the original ROS code, I would have to do this, which is what? Oh, it's a union. Oh, so it's not an enum. No, it's a tagged union. That's what they are. If you want them to hold values, they're tagged unions. Stop calling them enums. They're not that. So another problem with Rust is the fact that regular enums that are just integer types are also the same types as tagged

unions. For some reason they're treated as the same thing. Well that means we need to use derive on both of them for some reason. One is very complicated a tagged union. They use generics. So you have to work out on compile time what they are and generate the code. Whereas regular enums are just integers. Why do you need why can't you just hardcode them and just print them like it? It's simple. It should be very simple to compare them. They're just integers and

it's very easy to print them as well. You don't need all this complication just for enums. Another problem is that in the standard library, they have all of these drives. So every time you use an optional type or a result type, it will have to print out all of this. So let's say for example we have so if you do for example a result type with a string and an IO error it will generate this kind of code quite a lot 70 lines 70 80 lines

so so let's say for example you create a 100 of these in your project something like this well so 70 lines of code for each derived function to be generated and you have a 100 of them that's 7,000 lines of code the compiler has to generate and that's just the result type also for option type any enum you make it will have to generate the same code for each drive and you wonder why compile time is slow in Rust right so I

was coding in C++ and I generally hate header files which I can make another video about if people want to know why uh and I thought maybe I could make some project that will automate header files for me so I thought oh why not try Rust you know I'll give it a go I'll give it a fair try so I got an LLM to generate something that will uh basically loop through a directory and then find all the files of that with CBP extension and it gave me this code which I call

function callion where instead of going inside a dream inside a dream inside a dream inside a dream you go inside a function call inside a function call inside a function call inside a function call inside a function call for entry which it doesn't even tell you you can't even like so it's it's a directory entry can I do this can I do No, no. Why can't I do that? Infer types are better. Apparently, I can't even write the type. Okay, so thanks Rust. I

have to hover over all the time. So, we have new, which is a function. And this change to into iter. So, we're converting it into an iterator. And iterators are very complicated in Rust really. They're basically a strct that implements the trait, an interface of uh next, whatever that means. I don't really understand it. It's too complicated for me. Again, people are going to say skill issue, but I prefer

simplicity. This is not simple. So, we convert it to an iterator. Okay. Then we have a filter map result. Okay. I don't even know what this means. I guess result is like if it's not an error. So, so we convert to an iterator and we make sure it's not an error and we filter that with E in this whatever this means. E.file type is is it okay? Is it a file and is it a e.path.extension.mmap

or three function calls in a row x for extension equals cpp and then out of that I don't even know. Okay. So what I'm going to do I'm going to show you how complicated this is. First of all how do I even reason through this? Like first I need an iterator. Then I need a filter map. Then I needed filter. Then what are these types? What are they returning? How do I what if there's a bug? How do I debug

it? Good luck. Good luck is the answer. So what I tried to do was actually separate this into sections and give it types. So I'll show you what I did. So first we have entry iterator is a uh walk directory into iter. There is also an an into iter in the actual standard library. So this is a a walk directory into it. And that goes war directory new folder path. into it. So we have an into it which is a strct

which has all this stuff and it implements the trait again we got this derive stuff it implements the trait of next rust isn't too complicated right uh anyway so it's an iterator that can somehow convert what I want into files somehow somewhere I don't know it's hidden magic uh then we get an entry filter map which is a filter map of into it uh fn return or fn result directory entry war directory error and this returns an optional directory entry it's it's not too complicated rust right cuz I cuz I definitely know what a

filter map into it fn I don't even understand what the type is and then we get to the creme de creme of this so This is a filter filter map. But here's the best thing. Let's try to copy this, shall we? Let's try to We want to We want to specify the type, right? We want to specify the type. So, let's specify the type. Let's do this. Specify the type. And it's okay. It's giving me errors. Why is it giving me errors?

Cannot find type filter in this scope. So, what what's filter? Anyway, the errors aside, fixing the errors aside, it's literally literally impossible to write the type here. Why? Because it's generated at compile time. You don't actually know what the type is until the compiler actually writes the code. So, you literally cannot write the type. This is hidden magic. Like, the compiler literally generates this at compile time. There's no way you can even write

the type no matter what you do. So, it's just hidden magic. What's the type? It it filter filter map into iterator fn result directory entry error and it returns an optional directory entry implement fn mute at directory entry. What? >> But why why would you do that? Why would you do any of that? >> I just want to look through a directory. Did I does is Einstein expected to understand this code? And then here so we have four entry in.

So you can't even specify the type. So after I have to specify the type after so I can actually write the type otherwise I can't write it. So I have to actually you know create a copy of it. Let end directory directory entry and then okay then I can specify the type here like why would you why and of course and then we have more function callion at the end we sdfs read to string path.exect expect which will just crash if it you know doesn't find that

and we have content. to take dot collect function callion. So here is how I wrote this code. All right. So we have a directory entry in entries. Again, this is kind of using magic because entries itself is a redirectory. And if I go to redirectory where's the actual like the stuff you can where's the is it an array? Is it is it a list? Is it a box or how do I use the index? You literally are forced to

use iterators which I don't like. I want to use loops with the index, but apparently I can't do that. I I'm forced to use an iterator and then I can't specify the type again. I can't specify the type with something here. No, I got to do it after I've got to copy the variable to actually specify the type. Say, oh, don't specify the type. You know, it's it's, you know, it's smaller. It's I want to I want to understand the

code, especially when I don't know what the error type is. And the best thing is when I hover over this, it just says error. What's error? What's that? It's an SDI stdio error. And what's an SDIO error? It's a strruct with a rip rip. What's RIP? I'm This is overengineered, right? Anyway, so we go over that. We get the entry. Uh which I I find this really

weird to be honest. Um I generally don't like match cases or stuff like this. Anyway, uh so if there's an error, we do this. Otherwise we we uh basically get the path which is a path buff which is again another strct which has an OS string apparently. Anyway uh then we we recursively call this function if it's a folder otherwise we process CPP file. Uh notice how I haven't used function called seption and I've used uh I've specified every type here. Uh we just

display this we read the string and then we pass the file and pass the file uses a lot of other stuff. Um anyway, this is how I like to write stuff and Rust actively fights me the whole time. Which is my problem with it. If I try to write stuff like this, like people say, "Oh, that's not how you write Rust. What are you doing writing how I want to write code?" So, my general complaints about Rust aren't anything to do with safety

or the borrow checker. It's generally just it's overengineered, overly complicated, and I can't write the way I want to. That's my main problem with it. So, I don't find it enjoyable to write in. and the language actively fights me when I try to. So, there are some other problems I found while using Rust, which I'll show now. So, I made a video comparing languages in a chess move generator to test performance. And I ran

across a very, very annoying problem in Rust, which was stack overflows. So, in chess engines, you use massive constants for bishop and rook moves. It's the fastest way to get those kind of moves. You just use giant constants. So I tried running this in debug mode and it would give me a stack overflow. We don't even need the chess code to actually show this. So this is literally all the code we need. Um so we have a 200,000 sized

array and we literally just get one entry out of that and then return it and then print it. That's literally all we're doing. Have a guess what's going to happen. So just to prove it, let's go version Rust version 1.9. So, this is the latest version of Rust and we're going to go cargo run. Oh, we got Stack Overflow. Oh, h strange. Okay, let's run it in release mode. What? Basically, the problem is that uh

in debug mode, it will put constants on the stack and give you a stack overflow if they're too big. This is supposed to be a language like this should never happen. Like it doesn't matter like this. It should never happen. It it should run in debug mode and release mode. They should both run. This makes no sense at all. Why? Why? Plus, oh, you oh, increase the stack size. It shouldn't be on the

stack. It's a constant. It should be in global space. What What is wrong with this? So, you're able to write the most complicated compiler that can track when variables are created and when they're destroyed and when they're referenced somewhere else and then delete the old one. You can do all that, but you can't put constants on the global space and not give a stack overflow. Come on. And you could argue, oh, this is LLVM. Rust

converts to LLVM. Maybe it's LVM's fault. C++ and Zig both convert to LLVM. I'll convert this to ZIG and show you it will run in both modes. And we run this in zig. Let's go. Zigg run main.zig. Oh, look. It run. No stack overflow. Okay, let's run it in release mode. Minus O release fast. Oh, look. It runs. They both convert to LVM. This is a rust problem.

Right. So, here's the basic chess engine uh code. It's just we have constants in the global global space and we just have run perf and perf in line is this massive function that just generates moves plays them all. That's all it does. We're using uh global variables because that's what I found was the fastest. I tried putting in the strruct into the function and it was actually slower or just slightly slower but I couldn't get the performance any higher than what I got. So someone I'll

probably put his name on the screen on GitHub basically made the code a lot better well a lot faster and what did he do? Did he change the code? Not really. Let's have a look. So first we have engine just all the strcts basically one strct and then we implement engine and put all the we put all the functions inside methods inside strct and somehow it was 40% faster. What? So you it makes no sense. I mean

you could say oh it's LVM. No, it's not LVM because Zigg has exactly the same thing where you could put them in methods of a strruct or you could put them in just you know procedurally in global space functions and just pass a uh and just pass a structure to them or use global variables. The performance would be basically similar or the same really there's not much difference 40%. What is wrong with this compiler? So if

you make if you use procedural code and just use functions it's 40% slower. What is this? Anyway, that's my thoughts on Rust. It's generally just not for me. It's not my kind of language. Most things are just overly complicated. And my main complaint is the fact that I can't code the way I want to and the language actively fights me if I do. And other Rust users will say I'm coding it wrong. So, I'll go code in another

language then and not do it wrong. Of course, if you like Rust, that's fine. Go code in it. I I don't think it's a bad language. It works. It's just not for me. It was also ridiculously difficult to make with the compiler. Anyway, that's all for this video. Thanks for watching.

